import logging
import cherrypy
import os
from PIL import Image, ImageEnhance, ImageOps
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

import logging
#logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s ", level=logging.DEBUG)
#logging.info("test")


# Format cherrypy logging with ms output
cherrypy._cplogging.LogManager.time = lambda self : "" # Hack that cherrypy will not add a date/time to the message
new_formatter = logging.Formatter("%(asctime)s %(levelname)s:%(message)s")
for h in cherrypy.log.error_log.handlers:
    h.setFormatter(new_formatter)
cherrypy.log.error_log.setLevel(logging.DEBUG)
logging.getLogger().setLevel(logging.DEBUG)


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
        if ser_port_name_top is not None:
            try:
                self.ser_port_top = Serial(port=ser_port_name_top, baudrate=1000000, timeout=0.5, write_timeout=0.5)
                log_info(f"Opened {ser_port_name_top} for up link")
            except serialutil.SerialException:
                log_error(f"Unable to open serial port {ser_port_name_top}")
                self.system_error_msg = f"Unable to open serial port {ser_port_name_top}"

        if ser_port_name_bottom is not None:
            try:
                self.ser_port_bottom = Serial(port=ser_port_name_bottom, baudrate=1000000, timeout=0.5, write_timeout=0.5)
                log_info(f"Opened {ser_port_name_bottom} for down link")
            except serialutil.SerialException:
                log_error(f"Unable to open serial port {ser_port_name_bottom}")
                self.system_error_msg = f"Unable to open serial port {ser_port_name_bottom}"
        
        # Detect modules
        self.find_modules()

        # DEBUG: Send reset message continously
        #while True:
        #    self.send_ping()
        #    time.sleep(0.1)

        # DEBUG: Send a test message
        #while True:
        #    msg = Message(MESSAGE_TYPE_PING)
        #    self.send_message_retry(0, msg, 10)
        #    time.sleep(1)
        # DEBUG: Send test status codes
        #while True:
        #    for k in range(256):
        #        msg = Message(MESSAGE_TYPE_STAT, [k], 0)
        #        self.send_message_module(0, msg, False)
        #        time.sleep(1)
        #        log_error("send...")
    
    def find_modules(self):
        log_info("Initializing modules...")
        self.module_port_addr_mirror = []  # converts module_nr to port, address, and mirror flag

        # Debug - just add a dummy module
        #self.module_port_addr_mirror.append({"port": self.ser_port_top, "addr": 0, "mirror": False}) # Add a fake module instead
        #return


        # Assign addresses to each module on each string until noone responds any more
        port_list = [self.ser_port_top, self.ser_port_bottom]
        port_name_list = ["top", "bottom"]
        module_cnt = [0, 0]
        mirror = [True, False]
        for p in range(len(port_list)):
            port = port_list[p]
            port_name = port_name_list[p]
            if port is None:
                log_error(f"Skipping detection of modules on port {port_name} port as it is not opened")
                continue

            # Disable the return path for all modules
            self.send_ret_disable(port, MESSAGE_ADDR_BROADCAST)

            # Reset all module addresses to 0
            self.send_addr_set(port, MESSAGE_ADDR_BROADCAST, 0)
            
            addr = 1  # First module address is 1, as 0 is used as reset address
            while True:
                # Send the new address to the next module
                self.send_addr_set(port, 0, addr)

                # Enable the return path of that new module
                self.send_ret_enable(port, addr)

                # Send a ping to see if the module does exist
                if not self.send_ping(port, addr):
                    # No answer from this module, break the addressing loop
                    break
                # Otherwise add this module to the list
                self.module_port_addr_mirror.append({"port": port, "addr": addr, "mirror": mirror[p]})

                # And disable the return path of this module again
                self.send_ret_disable(port, addr)

                addr += 1
            addr -= 1
            log_info(f"Found {addr} modules on {port_name} port")

            # Now tell the last module of this string to switch on its return path
            if not self.send_ret_enable(port, addr):
                log_error(f"Unable to enable return path for module {addr} on port {port_name}")
                # TODO: This is a critical error which should be reported to the user. We need a queue back to the ModuleController for this error messages
                continue
            module_cnt[p] = addr
        # TODO: Report the module_cnt back to ModuleController - we also need a queue here...

    
    # Send a new address value to a module
    def send_addr_set(self, port, addr, new_addr):
        log_debug(f"Sending new address {new_addr} to {addr} on port {port.port}")
        msg = Message(MESSAGE_TYPE_ADDR_SET, [new_addr], addr)
        return self.send_message_port(port, msg, False)

    # Send MESSAGE_TYPE_RET_DISABLE message to a module
    def send_ret_disable(self, port, addr):
        msg = Message(MESSAGE_TYPE_RET_DISABLE, [], addr)
        # Send this message twice to make absolutely sure every module got it
        log_debug(f"Sending return disable message to {addr} on {port.port}")
        self.send_message_port(port, msg, False)
    
    # send MESSAGE_TYPE_RET_ENABLE to a module
    def send_ret_enable(self, port, addr):
        msg = Message(MESSAGE_TYPE_RET_ENABLE, [], addr)
        # Send this message twice to make absolutely sure every module got it
        log_debug(f"Sending return enable message to {addr} on {port.port}")
        self.send_message_port(port, msg, False)
    
    def send_ping(self, port, addr):
        msg = Message(MESSAGE_TYPE_PING, [], addr)
        log_debug(f"Sending ping to {addr} on {port.port}")
        return self.send_message_port(port, msg, True)

    def send_message_module(self, module_nr: int, msg: Message, expect_ack = True):
        # Convert module_nr to the serial port and the module address
        port = self.module_port_addr_mirror[module_nr]["port"]
        addr = self.module_port_addr_mirror[module_nr]["addr"]
        msg.dst = addr
        
        # Send message on the corresponding port
        return self.send_message_port(port, msg, expect_ack)
    
    def send_message_port(self, port: Serial, msg: Message, expect_ack: bool = True):
        log_info("Sending message: 0x" + msg.to_bytes().hex())

        # Make sure the port is opened
        if port is None:
            log_error("Unable to send message: Port not opened")
            return False

        # Make sure input buffer is empty
        port.reset_input_buffer()

        # Send message
        port.write(msg.to_bytes())
        log_info("Message sent")

        # If not ACK is expected, we are done at this point
        if not expect_ack:
            log_info("Not expecting ACK...")
            return True

        log_info("Waiting for ACK")
        # Wait for ACK
        ans = self.get_message(port)
        if ans is None:
            return False
        
        # Check answer
        if ans.type != MESSAGE_TYPE_ACK:
            log_error(f"Got message, but no ACK:")
            print(ans.to_bytes())
            return False
        
        # Got an ACK
        return True

    def get_message(self, port: Serial):
        log_info("Receiving message")

        # Make sure the port is opened
        if port is None:
            log_error("Unable to send message: Port not opened")
            return False
        
        # Wait for magic byte
        while True:
            data = port.read(1)
            if len(data) != 1:
                log_debug("Failed to get magic byte from module: Timeout")
                return None
            if data[0] != MESSAGE_MAGIC:
                log_error(f"Lost sync, got {data} instead of {MESSAGE_MAGIC}")
                continue
            else:
                break
        # Magic byte received
        ans = Message()
        ans.magic = MESSAGE_MAGIC
        log_info("Got magic byte")

        # Read header
        header = port.read(5)
        if len(header) != 5:
            log_error("Failed to read message header from module: Timeout")
            return None
        ans.type = header[0]
        ans.src = header[1]
        ans.dst = header[2]
        ans.len = header[4]*256 + header[3]
        log_info(f"Got header: {ans.to_bytes().hex()}")
        if ans.len > MESSAGE_MAX_DATA_SIZE:
            log_error(f"Got message header with too high len value of {ans.len}")
            return None
        
        # Read the data
        if ans.len > 0:
            log_info(f"Reading payload of length {ans.len}")
            data = port.read(ans.len)
            log_debug(f"Got payload: 0x{data.hex()}")
            if len(data) != ans.len:
                log_error(f"Failed to receive {ans.len} bytes of data, got only {len(ans.data)} bytes")
                return None
            ans.data = np.frombuffer(data, dtype=np.uint8)
            log_debug("Got data")

        # Answer is complete
        return ans
    
    def send_image_data(self, module_nr: int, img_data: np.array):
        # Mirror image data if required
        module = self.module_port_addr_mirror[module_nr]
        if module["mirror"]:
            img_data = np.flipud(img_data)
        message = Message(MESSAGE_TYPE_DATA, img_data)
        self.send_message_module(module_nr, message)


class ModuleController(Thread):
    def __init__(self, config, command_queue):
        Thread.__init__(self, daemon=True)
        self.command_queue = command_queue
        self.router = PacketRouter(config["port_up"], config["port_down"])
        self.uploading_image = False
        self.playing = False
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
            "mirror": False,
            "allow_scaling": True,
            "repeat": False,
            "pixel_mode": True,
            "image_hash": "01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b",
            "progress_status": "noimage",
            "progress_value": 0.0,
            "progress_msg": "",
            "system_error_msg": ""
        }

        # The system error message may have been set during initialization of the packet router
        self.led_settings["system_error_msg"] = self.router.system_error_msg

        # Scale and upload the current image
        self.update_image()

    def run(self):
        while True:
            command_data = self.command_queue.get()
            log_info("Got command: " + command_data["command"])
            if command_data["command"] == "init_modules":
                # Send a reset command
                self.router.find_modules()
            elif command_data["command"] == "save_image":
                self.update_progress("processing", "Saving image", 0.0)
                # Convert image to RGB
                self.image = self.image.convert("RGB")
                # Save new original image as png
                # The compression level is chosen fairly low to speed things up
                self.image.save("image.png", compress_level=1)
                log_info("Saved original image")
            elif command_data["command"] == "update_image":
                self.update_progress("processing", "Scaling image", 0.2)
                log_info("Processing new image")

                # Apply color temperature correction
                temp_sel = self.led_settings['color_temperature']
                # Get the closest RGB values from the table
                r, g, b = get_color_temperatures(temp_sel)
                matrix = (r/255.0, 0.0, 0.0, 0.0,
                    0.0, g/255.0, 0.0, 0.0,
                    0.0, 0.0, b/255.0, 0.0)
                image_scaled = self.image.convert('RGB', matrix)
                log_info(f"Applied color temperature of {temp_sel} K")

                # Apply brightness correction
                enhancer = ImageEnhance.Brightness(image_scaled)
                log_info(f"Brightness: {self.led_settings['brightness']}")
                image_scaled = enhancer.enhance(self.led_settings["brightness"])
                log_info(f"Applied brightness of {self.led_settings['brightness']*100}%")

                # TODO: Crop image if required

                # Scale image
                # TODO: Only if it has to be rescaled...
                width = round(self.height*self.image.size[0]/self.image.size[1])
                image_scaled = image_scaled.resize((width, self.height))
                log_info(f"Image resized to {width}x{self.height}")

                # Mirror image
                if self.led_settings["mirror"]:
                    image_scaled = ImageOps.mirror(image_scaled)

                # Save scaled image
                image_scaled.save("image_scaled.png")
                log_info("Saved scaled image")

                # Calculate the hash of the scaled image
                image_bytes = image_scaled.tobytes()
                self.led_settings["image_hash"] = hashlib.sha256(image_bytes).hexdigest()
                log_info(f"New hash: {self.led_settings['image_hash']}")
                log_info("Updated scaled image hash")
            elif command_data["command"] == "upload_image":
                self.uploading_image = True
                self.update_progress("processing", "Uploading image", 0.4)
                for k in range(10):
                    log_info(f"Uploading image... {k+1}/10")
                    time.sleep(0.2)
                    self.led_settings["progress_value"] = 0.4+0.6*k/9
                    if not self.uploading_image:
                        log_info("Cancelled upload")
                        self.update_progress("noimage", "", 0.0)
                        break
                self.update_progress("ready", "", 0.0)
            elif command_data["command"] == "set_speed":
                # TODO: Send new speed value to microcontroller
                log_info(f"Set speed to {self.led_settings['speed']} m/s")
            elif command_data["command"] == "set_repeat":
                # TODO: Send new repeat value to microcontroller
                log_info(f"Sent repeat value of {self.led_settings['repeat']} to modules")
            elif command_data["command"] == "set_pixel_mode":
                # TODO: Send new pixel_mode value to microcontroller
                log_info(f"Sent pixel_mode value of {self.led_settings['pixel_mode']} to modules")
            elif command_data["command"] == "trigger":
                self.led_settings["progress_status"] = "playing"
                self.led_settings["progress_value"] = 0.0
                self.playing = True
                delay = self.led_settings['trigger_delay']
                log_info(f"Got trigger command, will spleep {delay} s")
                slept = 0.0
                while slept < self.led_settings['trigger_delay']:
                    time.sleep(0.05)
                    slept += 0.05
                    self.led_settings["progress_value"] = slept/delay
                    if not self.playing:
                        self.led_settings["progress_status"] = "ready"
                        break
                self.led_settings["progress_value"] = 0.0
                if not self.playing:
                    continue
                # TODO: Send trigger to microcontroller
                log_info(f"Triggered")

                # Fake loading bar for playback
                # TODO: Find something how we can know the current state without estimating it
                for k in range(10):
                    self.led_settings["progress_value"] = k/9.0
                    time.sleep(1)
                    if not self.playing:
                        break
                self.led_settings["progress_status"] = "ready"
                self.led_settings["progress_value"] = 0.0


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
        log_info(f"Set trigger delay to {self.led_settings['trigger_delay']} s")
    
    def set_mirror(self, mirror):
        self.led_settings["mirror"] = mirror
        # Update the image
        self.update_image()
    
    def set_repeat(self, repeat):
        self.led_settings["repeat"] = repeat
        # Send repeat value to modules
        self.command_queue.put({"command": "set_repeat"})
    
    def set_allow_scaling(self, allow_scaling):
        self.led_settings["allow_scaling"] = allow_scaling
        # Update the image
        self.update_image()

    def set_pixel_mode(self, pixel_mode):
        self.led_settings["pixel_mode"] = pixel_mode
        # Send pixel_mode value to modules
        self.command_queue.put({"command": "set_pixel_mode"})

    
    def trigger(self):
        if self.playing:
            # Stop current playback
            self.playing = False
        else:
            # Start playback
            self.command_queue.put({"command": "trigger"})


class WebServer(object):
    def __init__(self, config):
        self.config = config
        self.command_queue = Queue()
        self.controller = ModuleController(config, self.command_queue)
        self.controller.start()
        log_info("BlinkyBar server started")

    # Load index.html
    @cherrypy.expose
    def index(self):
        return open(os.path.join(static_dir, "index.html"))
    
    @cherrypy.expose
    def settings(self, speed=None, brightness=None, trigger_delay=None, mirror=None, allow_scaling=None, repeat=None, color_temperature=None, pixel_mode=None):
        # Create a copy of the current settings dict
        retval = dict(self.controller.led_settings)
        retval["success"] = False
        retval["error_msg"] = ""

        # Check all the variables first
        if speed is not None:
            try:
                speed = float(speed)
            except ValueError:
                retval["error_msg"] = "Speed is not a float"
                return ujson.dumps(retval, indent=4)
            if speed < 0.1 or speed > 100:
                retval["error_msg"] = "Speed is out of range"
                return ujson.dumps(retval, indent=4)
        if brightness is not None:
            try:
                brightness = float(brightness)
            except ValueError:
                retval["error_msg"] = "Brightness is not a float"
                return ujson.dumps(retval, indent=4)
            if brightness < 0.1 or brightness > 1.0:
                retval["error_msg"] = "Brightness is out of range"
                return ujson.dumps(retval, indent=4)
        if color_temperature is not None:
            try:
                color_temperature = float(color_temperature)
            except ValueError:
                retval["error_msg"] = "Color temperature is not a float"
                return ujson.dumps(retval, indent=4)
            if color_temperature < 1000 or color_temperature > 10000:
                retval["error_msg"] = "Color temperature is out of range"
                return ujson.dumps(retval, indent=4)
        if trigger_delay is not None:
            try:
                trigger_delay = float(trigger_delay)
            except ValueError:
                retval["error_msg"] = "Trigger delay is not a float"
                return ujson.dumps(retval, indent=4)
            if trigger_delay < 0 or trigger_delay > 1000.0:
                retval["error_msg"] = "Trigger delay is out of range"
                return ujson.dumps(retval, indent=4)
        if mirror is not None:
            if mirror.lower() in ['true', '1',]:
                mirror = True
            elif mirror.lower() in ['false', '0',]:
                mirror = False
            else:
                retval["error_msg"] = "mirror is out of range"
                return ujson.dumps(retval, indent=4)
        if repeat is not None:
            if repeat.lower() in ['true', '1',]:
                repeat = True
            elif repeat.lower() in ['false', '0',]:
                repeat = False
            else:
                retval["error_msg"] = "repeat is out of range"
                return ujson.dumps(retval, indent=4)
        if allow_scaling is not None:
            if allow_scaling.lower() in ['true', '1',]:
                allow_scaling = True
            elif allow_scaling.lower() in ['false', '0',]:
                allow_scaling = False
            else:
                retval["error_msg"] = "allow_scaling is out of range"
                return ujson.dumps(retval, indent=4)
        if pixel_mode is not None:
            if pixel_mode.lower() in ['true', '1',]:
                pixel_mode = True
            elif pixel_mode.lower() in ['false', '0',]:
                pixel_mode = False
            else:
                retval["error_msg"] = "pixel_mode is out of range"
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
        
        if mirror is not None:
            self.controller.set_mirror(mirror)
        
        if repeat is not None:
            self.controller.set_repeat(repeat)
        
        if pixel_mode is not None:
            self.controller.set_pixel_mode(pixel_mode)

        if allow_scaling is not None:
            self.controller.set_allow_scaling(allow_scaling)

        # Get the current settings and return them
        retval = dict(self.controller.led_settings)
        retval["success"] = True
        return ujson.dumps(retval, indent=4)

    # Upload an image as png/jpg/gif/... in post data
    @cherrypy.expose
    def set_image(self, image_obj):
        log_info("Got a new image")
        image_data = image_obj.file.read()

        log_info("set_image data read")
        new_image = Image.open(io.BytesIO(image_data))
        self.controller.new_image(new_image)
        log_info("set_image processed")
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
        self.controller.trigger()
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

    log_info("Started BlinkyBar Server")

    static_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')
    conf = {
        '/': {
            'tools.staticdir.root': static_dir,
            'tools.staticdir.on': True,
            'tools.staticdir.dir': ''
        }
    }
    cherrypy.quickstart(WebServer(config), '/', conf)
