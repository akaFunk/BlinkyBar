import logging
import cherrypy
import os
from PIL import Image, ImageEnhance
import ujson
import io
from serial import Serial, serialutil
from threading import Thread
import time
from queue import Queue
import datetime
import hashlib
import configparser
import numpy as np
from message import *
from colortemperaturetable import *


# Format cherrypy logging with ms output
cherrypy._cplogging.LogManager.time = lambda self : "" # Hack that cherrypy will not add a date/time to the message
new_formatter = logging.Formatter("%(asctime)s %(levelname)s:%(message)s")
for h in cherrypy.log.error_log.handlers:
    h.setFormatter(new_formatter)
cherrypy.log.error_log.setLevel(logging.DEBUG)


def log_fatal(msg):
    cherrypy.log(msg, severity=logging.FATAL)

def log_error(msg):
    cherrypy.log(msg, severity=logging.ERROR)

def log_warn(msg):
    cherrypy.log(msg, severity=logging.WARN)

def log_info(msg):
    cherrypy.log(msg, severity=logging.INFO)

def log_debug(msg):
    cherrypy.log(msg, severity=logging.DEBUG)


# The packet router will abstract the two strings of modules and the module orientation. It will
# initialize the modules, give them an address. The class will provide the number of modules
# available and the height in pixels. It also converts the module_nr to the correct string and
# module address. The module_nr is a number identifying the modules starting at the top with 0
# and counting up for modules below that.
# When you send data to one of the modules, PacketRouter will automatically mirror the data for
# the upper bar.
class PacketRouter:
    def __init__(self, ser_port_name_top=None, ser_port_name_bottom=None):
        # Initialize serial ports
        self.ser_port_name_top = ser_port_name_top
        self.ser_port_name_bottom = ser_port_name_bottom
        self.ser_port_top = None
        self.ser_port_bottom = None
        self.system_error_msg = ""

        # Open the ports
        try:
            self.ser_port_top = Serial(port=ser_port_name_top, baudrate=1000000, timeout=0.5, write_timeout=0.5)
        except serialutil.SerialException:
            log_error("Unable to open serial port")
            self.system_error_msg = f"Unable to open serial port {ser_port_name_top}"
            return
        log_debug(f"Opened {ser_port_name_top} for up link")

        try:
            self.ser_port_bottom = Serial(port=ser_port_name_bottom, baudrate=1000000, timeout=0.5, write_timeout=0.5)
        except FileNotFoundError:
            log_error("Unable to open serial port")
            self.system_error_msg = f"Unable to open serial port {ser_port_name_bottom}"
            return
        log_debug(f"Opened {ser_port_name_bottom} for down link")

        # TODO: Remove later, only for debugging with Arduino board
        # Wait for Arduino board reset
        log_debug("Waiting for arduino to reset...")
        time.sleep(3)
        
        # TODO: Find modules
        self.module_port_addr_mirror = []  # converts module_nr to port, address, and mirror flag
        self.module_port_addr_mirror.append({"port": self.ser_port_top, "addr": 0, "mirror": False}) # Add a fake module instead

        # DEBUG: Send a test message
        #while True:
        #    msg = Message(MESSAGE_TYPE_PING)
        #    self.send_message_retry(0, msg, 10)
        #    time.sleep(1)
    
    def init_modules(self):
        cherrypy.log("Initializing modules...")
    
    def send_message_retry(self, module_nr: int, msg: Message, expect_ack = True, retry_count: int = 1):
        for _ in range(retry_count):
            if self.send_message(module_nr, msg, expect_ack):
                return True
            log_error("Resending message...")
        log_error("Message was not ack'd after {retry_count} retries, giving up")
        return False

    def send_message(self, module_nr: int, msg: Message, expect_ack = True):
        # Convert module_nr to the serial port and the module address
        port = self.module_port_addr_mirror[module_nr]["port"]
        if port is None:
            cherrypy.log("Unable to send message: Port not opened")
            return False
        addr = self.module_port_addr_mirror[module_nr]["addr"]
        msg.dst = addr
        
        # Make sure input buffer is empty
        port.reset_input_buffer()

        # Send message
        port.write(msg.to_bytes())
        log_debug("Message sent")

        # If not ACK is expected, we are done at this point
        if not expect_ack:
            return True

        # Wait for ACK
        ans = self.get_message(port)
        if ans is None:
            return False
        
        # Check answer
        if ans.type != MESSAGE_TYPE_ACK:
            log_error("Got message, but no ACK")
            return False
        
        # Got an ACK
        return True

    def get_message(self, port: Serial):
        log_debug("Receiving message")
        # Wait for magic byte
        while True:
            data = port.read(1)
            if len(data) != 1:
                log_error("Failed to get magic byte from module: Timeout")
                return None
            if data[0] != MESSAGE_MAGIC:
                log_error(f"Lost sync, got {data} instead of {MESSAGE_MAGIC}")
                continue
            else:
                break
        # Magic byte received
        ans = Message()
        ans.magic = MESSAGE_MAGIC
        log_debug("Got magic byte")

        # Read header
        header = port.read(5)
        if len(header) != 5:
            log_error("Failed to read message header from module: Timeout")
            return None
        ans.type = header[0]
        ans.src = header[1]
        ans.dst = header[2]
        ans.len = header[4]*256 + header[3]
        log_debug("Got header")
        if ans.len > MESSAGE_MAX_DATA_SIZE:
            log_error(f"Got message header with too high len value of {ans.len}")
            return None
        
        # Read the data
        ans.data = port.read(ans.len)
        if len(ans.data) != ans.len:
            log_error(f"Failed to receive {ans.len} bytes of data, got only {len(ans.data)} bytes")
            return None
        
        # Answer is complete
        return ans
    
    def send_image_data(self, module_nr: int, img_data: np.array):
        # Mirror image data if required
        module = self.module_port_addr_mirror[module_nr]
        if module["mirror"]:
            img_data = np.flipud(img_data)
        message = Message(MESSAGE_TYPE_DATA, img_data)
        self.send_message(module_nr, message)


class ModuleController(Thread):
    def __init__(self, config, command_queue):
        Thread.__init__(self, daemon=True)
        self.command_queue = command_queue
        self.router = PacketRouter(config["port_up"], config["port_down"])
        self.uploading_image = False
        self.image = Image.open("image.png")
        self.progress_extra_steps = 0
        self.height = 120 # TODO: This should come from the stick

        # TODO: After getting the size of the stick, the scaled image should be calculated

        self.led_settings = {
            "success": True,
            "error_msg": "",
            "brightness": 1.0,
            "speed": 2.0,
            "color_temperature": 6500,
            "trigger_delay": 1.0,
            "allow_scaling": True,
            "image_hash": "01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b",
            "progress_status": "noimage",
            "progress_value": 0.0,
            "progress_msg": "",
            "system_error_msg": ""
        }

        # The system error message may have been set during initialization of the packet router
        self.led_settings["system_error_msg"] = self.router.system_error_msg

        # Initialize the modules
        self.init_modules()

        # Scale and upload the current image
        self.update_image()

    def run(self):
        while True:
            command_data = self.command_queue.get()
            cherrypy.log("Got command: " + command_data["command"])
            if command_data["command"] == "init_modules":
                # Send a reset command
                self.router.init_modules()
            elif command_data["command"] == "save_image":
                self.update_progress("processing", "Saving image", 0.0)
                # Convert image to RGB
                self.image = self.image.convert("RGB")
                # Save new original image as png
                # The compression level is chosen fairly low to speed things up
                self.image.save("image.png", compress_level=1)
                cherrypy.log("Saved original image")
            elif command_data["command"] == "update_image":
                self.update_progress("processing", "Scaling image", 0.2)
                cherrypy.log("Processing new image")

                # Apply color temperature correction
                temp_sel = self.led_settings['color_temperature']
                # Get the closest RGB values from the table
                r, g, b = get_color_temperatures(temp_sel)
                matrix = (r/255.0, 0.0, 0.0, 0.0,
                    0.0, g/255.0, 0.0, 0.0,
                    0.0, 0.0, b/255.0, 0.0)
                image_scaled = self.image.convert('RGB', matrix)
                cherrypy.log(f"Applied color temperature of {temp_sel} K")

                # Apply brightness correction
                enhancer = ImageEnhance.Brightness(image_scaled)
                cherrypy.log(f"Brightness: {self.led_settings['brightness']}")
                image_scaled = enhancer.enhance(self.led_settings["brightness"])
                cherrypy.log(f"Applied brightness of {self.led_settings['brightness']*100}%")

                # TODO: Crop image if required

                # Scale image
                # TODO: Only if it has to be rescaled...
                width = round(self.height*self.image.size[0]/self.image.size[1])
                image_scaled = image_scaled.resize((width, self.height))
                cherrypy.log(f"Image resized to {width}x{self.height}")

                # Save scaled image
                image_scaled.save("image_scaled.png")
                cherrypy.log("Saved scaled image")

                # Calculate the hash of the scaled image
                image_bytes = image_scaled.tobytes()
                self.led_settings["image_hash"] = hashlib.sha256(image_bytes).hexdigest()
                cherrypy.log(f"New hash: {self.led_settings['image_hash']}")
                cherrypy.log("Updated scaled image hash")
            elif command_data["command"] == "upload_image":
                self.uploading_image = True
                self.update_progress("processing", "Uploading image", 0.4)
                for k in range(10):
                    cherrypy.log(f"Uploading image... {k+1}/10")
                    time.sleep(0.2)
                    self.led_settings["progress_value"] = 0.4+0.6*k/9
                    if not self.uploading_image:
                        cherrypy.log("Cancelled upload")
                        self.update_progress("noimage", "", 0.0)
                        break
                self.update_progress("ready", "", 0.0)
            elif command_data["command"] == "set_speed":
                # TODO: Send new speed value to microcontroller
                cherrypy.log(f"Set speed to {self.led_settings['speed']} m/s")
            elif command_data["command"] == "trigger":
                delay = self.led_settings['trigger_delay']
                cherrypy.log(f"Got trigger command, will spleep {delay} s")
                if delay != 0.0:
                    time.sleep(delay)
                # TODO: Send trigger to microcontroller
                cherrypy.log(f"Triggered")

    def init_modules(self):
        self.command_queue.put({"command": "init_modules"})

    def update_progress(self, status, msg, value):
        self.led_settings["progress_status"] = status
        self.led_settings["progress_msg"] = msg
        self.led_settings["progress_value"] = value

    def new_image(self, new_image):
        # Save the new image
        self.image = new_image
        # Save image to filesystem - asynchronously
        self.command_queue.put({"command": "save_image"})
        # Trigger an image update and uplload
        self.update_image()

    def update_image(self):
        # Update the scaled image - asynchronously
        self.command_queue.put({"command": "update_image"})
        # Trigger an image upload
        self.upload_image()

    def upload_image(self):
        # Cancel a currently running upload
        # TODO: This method is not perfect, if there are a lot of upload commands in a row it may happen that the image is uploaded multiple times
        if self.uploading_image:
            self.uploading_image = False
        # Add the image upload to the command queue - asynchronously
        self.command_queue.put({"command": "upload_image"})

    def set_speed(self, speed):
        self.led_settings["speed"] = speed
        self.command_queue.put({"command": "set_speed"})

    def set_brightness(self, brightness):
        self.led_settings["brightness"] = brightness
        # Update the image
        self.update_image()
    
    def set_color_temperature(self, color_temperature):
        self.led_settings["color_temperature"] = color_temperature
        # Update the image
        self.update_image()

    def set_trigger_delay(self, trigger_delay):
        self.led_settings["trigger_delay"] = trigger_delay
        cherrypy.log(f"Set trigger delay to {self.led_settings['trigger_delay']} s")
    
    def set_allow_scaling(self, allow_scaling):
        self.led_settings["allow_scaling"] = allow_scaling
        # Update the image
        self.update_image()
    
    def trigger(self, delay):
        self.command_queue.put({"command": "trigger"})


class WebServer(object):
    def __init__(self, config):
        self.config = config
        self.command_queue = Queue()
        self.controller = ModuleController(config, self.command_queue)
        self.controller.start()
        cherrypy.log("BlinkyBar server started")

    # Load index.html
    @cherrypy.expose
    def index(self):
        return open(os.path.join(static_dir, "index.html"))
    
    @cherrypy.expose
    def settings(self, speed=None, brightness=None, trigger_delay=None, allow_scaling=None, color_temperature=None):
        # Create a copy of the current settings dict
        retval = dict(self.controller.led_settings)
        retval.update(dict({"success:": False, "error_msg": ""}))

        # Check all the variables first
        if speed is not None:
            try:
                speed = float(speed)
            except ValueError:
                retval.update(dict({"error_msg": "Speed is not a float"}))
                return ujson.dumps(retval, indent=4)
            if speed < 0.1 or speed > 100:
                retval.update(dict({"error_msg": "Speed is out of range"}))
                return ujson.dumps(retval, indent=4)
        if brightness is not None:
            try:
                brightness = float(brightness)
            except ValueError:
                retval.update(dict({"error_msg": "Brightness is not a float"}))
                return ujson.dumps(retval, indent=4)
            if brightness < 0.1 or brightness > 1.0:
                retval.update(dict({"error_msg": "Brightness is out of range"}))
                return ujson.dumps(retval, indent=4)
        if color_temperature is not None:
            try:
                color_temperature = float(color_temperature)
            except ValueError:
                retval.update(dict({"error_msg": "Color temperature is not a float"}))
                return ujson.dumps(retval, indent=4)
            if color_temperature < 1000 or color_temperature > 10000:
                retval.update(dict({"error_msg": "Color temperature is out of range"}))
                return ujson.dumps(retval, indent=4)
        if trigger_delay is not None:
            try:
                trigger_delay = float(trigger_delay)
            except ValueError:
                retval.update(dict({"error_msg": "Trigger delay is not a float"}))
                return ujson.dumps(retval, indent=4)
            if trigger_delay < 0 or trigger_delay > 1000.0:
                retval.update(dict({"error_msg": "Trigger delay is out of range"}))
                return ujson.dumps(retval, indent=4)
        if allow_scaling is not None:
            if allow_scaling.lower() in ['true', '1',]:
                allow_scaling = True
            elif allow_scaling.lower() in ['false', '0',]:
                allow_scaling = False
            else:
                retval.update(dict({"error_msg": "allow_scaling is out of range"}))
                return ujson.dumps(retval, indent=4)

        # All values seem to be ok, update the state
        if speed is not None:
            self.controller.set_speed(speed)
        
        if brightness is not None:
            self.controller.set_brightness(brightness)
        
        if color_temperature is not None:
            self.controller.set_color_temperature(color_temperature)
        
        if trigger_delay is not None:
            self.controller.set_trigger_delay(trigger_delay)
        
        if allow_scaling is not None:
            self.controller.set_allow_scaling(allow_scaling)

        # Get the current settings and return them
        retval = dict(self.controller.led_settings)
        retval.update(dict({"success:": True, "error_msg": ""}))
        return ujson.dumps(retval, indent=4)

    # Upload an image as png/jpg/gif/... in post data
    @cherrypy.expose
    def set_image(self, image_obj):
        cherrypy.log("Got a new image")
        image_data = image_obj.file.read()

        cherrypy.log("set_image data read")
        new_image = Image.open(io.BytesIO(image_data))
        self.controller.new_image(new_image)
        cherrypy.log("set_image processed")
        return ujson.dumps({"success": True})
    
    # Download the full image
    @cherrypy.expose
    def get_image(self, fake_param = 0):
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "image.png")
        #cherrypy.response.headers['Content-Type'] = "image/png"
        return cherrypy.lib.static.serve_file(path)
    
    # Download the scaled image
    @cherrypy.expose
    def get_image_scaled(self, fake_param = 0):
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "image_scaled.png")
        return cherrypy.lib.static.serve_file(path)
    
    @cherrypy.expose
    def trigger(self):
        return ujson.dumps({"success": True})

if __name__ == '__main__':
    cfgparser = configparser.RawConfigParser()
    cfgparser.read("blinkybar.conf")
    config = dict()
    config["port_up"] = cfgparser.get("blinkybar", "port_up")
    if config["port_up"] == "none":
        config["port_up"] = None
    config["port_down"] = cfgparser.get("blinkybar", "port_down")
    if config["port_down"] == "none":
        config["port_down"] = None
    config["baudrate"] = float(cfgparser.get("blinkybar", "baudrate"))

    cherrypy.log("Started BlinkyBar Server")

    static_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')
    conf = {
        '/': {
            'tools.staticdir.root': static_dir,
            'tools.staticdir.on': True,
            'tools.staticdir.dir': ''
        }
    }
    cherrypy.quickstart(WebServer(config), '/', conf)
