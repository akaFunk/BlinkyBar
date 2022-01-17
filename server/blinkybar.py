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
from avrctrl import AvrCtrl
import RPi.GPIO as GPIO

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
# initialize the modules and give them an address. The class will provide the number of modules
# available and the height in pixels. It also converts the module_nr to the correct string and
# module address. The module_nr is a number identifying the modules starting at the top with 0
# and counting up for modules below that.
# When you send data to one of the modules, PacketRouter will automatically mirror the data for
# the upper bar.
class PacketRouter:
    def __init__(self, ser_port_name_top, ser_port_name_bottom, baudrate):
        # Initialize serial ports
        self.ser_port_name_top = ser_port_name_top
        self.ser_port_name_bottom = ser_port_name_bottom
        self.ser_port_top = None
        self.ser_port_bottom = None
        self.system_error_msg = ""

        # Open the ports
        if ser_port_name_top is not None:
            try:
                self.ser_port_top = Serial(port=ser_port_name_top, baudrate=baudrate, timeout=0.5, write_timeout=0.5)
                log_info(f"Opened {ser_port_name_top} for up link")
            except serialutil.SerialException:
                log_error(f"Unable to open serial port {ser_port_name_top}")
                self.system_error_msg = f"Unable to open serial port {ser_port_name_top}"

        if ser_port_name_bottom is not None:
            try:
                self.ser_port_bottom = Serial(port=ser_port_name_bottom, baudrate=baudrate, timeout=0.5, write_timeout=0.5)
                log_info(f"Opened {ser_port_name_bottom} for down link")
            except serialutil.SerialException:
                log_error(f"Unable to open serial port {ser_port_name_bottom}")
                self.system_error_msg = f"Unable to open serial port {ser_port_name_bottom}"
        
        # Detect modules
        self.find_modules()
    
    def find_modules(self):
        log_info("Initializing modules...")
        self.module_port_addr_mirror = []  # converts module_nr to port, address, and mirror flag

        port_list = [self.ser_port_top, self.ser_port_bottom]
        port_name_list = ["top", "bottom"]
        module_cnt = [0, 0]
        mirror = [False, True]
        for p in range(len(port_list)):
            port = port_list[p]
            port_name = port_name_list[p]
            if port is None:
                log_error(f"Skipping detection of modules on port {port_name} as it is not opened")
                continue

            # Disable the return path for all modules
            log_info(f"Disabling all return paths on port {port_name}")
            self.send_ret_disable(port, MESSAGE_ADDR_BROADCAST)

            # Reset all module addresses to 0
            log_info(f"Resetting all module addresses on port {port_name}")
            self.send_addr_set(port, MESSAGE_ADDR_BROADCAST, 0)

            # Send all modules their address - we support up to 20 modules
            MAX_MODULE_CNT = 3  # TODO: This should be a configuration parameter
            for addr in range(1, MAX_MODULE_CNT+1):
                self.send_addr_set(port, 0, addr)

            # Now enable the return path, starting from the last module until we get an answer
            found_module = False
            for addr in range(MAX_MODULE_CNT, 0, -1):
                if self.send_ret_enable(port, addr):
                    log_info(f"Got answer from module {addr}")
                    found_module = True
                    break
            if not found_module:
                module_cnt[p] = 0
            else:
                module_cnt[p] = addr

            # Add the modules to the list. For un-mirrored modules, we need to add the last module in
            # the chain as the first one to the global list.
            if not mirror[p]:
                for addr in range(module_cnt[p], 0, -1):
                    self.module_port_addr_mirror.append({"port": port, "addr": addr, "mirror": mirror[p]})
            else:
                for addr in range(1, module_cnt[p]+1):
                    self.module_port_addr_mirror.append({"port": port, "addr": addr, "mirror": mirror[p]})
            log_info(f"Found a total of {module_cnt[p]} modules on port {port_name}")

        # TODO: Report the module_cnt back to ModuleController - we also need a queue here...

    # Returns the number of detected modules
    def get_num_modules(self):
        return len(self.module_port_addr_mirror)
    
    # Send a new address value to a module
    def send_addr_set(self, port, addr, new_addr):
        log_debug(f"Sending new address {new_addr} to {addr} on port {port.port}")
        msg = Message(MESSAGE_TYPE_ADDR_SET, [new_addr], addr)
        return self.send_message_port(port, msg, False)

    # Send MESSAGE_TYPE_RET_DISABLE message to a module
    def send_ret_disable(self, port, addr):
        msg = Message(MESSAGE_TYPE_RET_DISABLE, [], addr)
        log_debug(f"Sending return disable message to {addr} on {port.port}")
        self.send_message_port(port, msg, False)
    
    # send MESSAGE_TYPE_RET_ENABLE to a module
    def send_ret_enable(self, port, addr):
        msg = Message(MESSAGE_TYPE_RET_ENABLE, [], addr)
        log_debug(f"Sending return enable message to {addr} on {port.port}")
        return self.send_message_port(port, msg)
    
    def send_ping(self, port, addr):
        msg = Message(MESSAGE_TYPE_PING, [], addr)
        log_debug(f"Sending ping to {addr} on {port.port}")
        return self.send_message_port(port, msg)

    def send_state(self, port, addr, value):
        msg = Message(MESSAGE_TYPE_STAT, [value], addr)
        log_debug(f"Sending state {value} to {addr} on {port.port}")
        return self.send_message_port(port, msg)

    def send_pixel_mode(self, module_nr, pixel_mode:bool):
        msg = Message(MESSAGE_TYPE_PIXEL_MODE, [pixel_mode])
        return self.send_message_module(module_nr, msg, True)

    # Turn off all LEDs on all ports by sending a state to each module
    def send_reset_leds(self):
        for t in self.module_port_addr_mirror:
            self.send_state(t["port"], t["addr"], 0)
    
    # Send a prepare message, which will cause the modules to load the first image column
    # from flash into ram.
    def send_prep(self, module_nr: int):
        msg = Message(MESSAGE_TYPE_PREP)
        return self.send_message_module(module_nr, msg)
    
    # Send a trigger message a module
    # Note: This is only for debug purposes, the modules are normally triggered by 
    # a hardware line all together and with proper timing.
    def send_trig(self, module_nr: int):
        msg = Message(MESSAGE_TYPE_TRIG)
        return self.send_message_module(module_nr, msg)

    def send_message_module(self, module_nr: int, msg: Message, expect_ack = True):
        # Convert module_nr to the serial port and the module address
        port = self.module_port_addr_mirror[module_nr]["port"]
        addr = self.module_port_addr_mirror[module_nr]["addr"]
        msg.dst = addr
        
        # Send message on the corresponding port
        return self.send_message_port(port, msg, expect_ack)
    
    def send_message_port(self, port: Serial, msg: Message, expect_ack: bool = True):
        log_debug("Sending message: 0x" + msg.to_bytes().hex())

        # Make sure the port is opened
        if port is None:
            log_error("Unable to send message: Port not opened")
            return False

        # Make sure input buffer is empty
        port.reset_input_buffer()

        # Send message
        port.write(msg.to_bytes())
        log_debug("Message sent")

        # If not ACK is expected, we are done at this point
        if not expect_ack:
            log_debug("Not expecting ACK...")
            return True

        log_debug("Waiting for ACK...")
        # Wait for ACK
        ans = self.get_message(port)
        if ans is None:
            log_debug("Got no ACK")
            return False
        
        # Check answer
        if ans.type != MESSAGE_TYPE_ACK:
            log_error(f"Got message, but no ACK: {ans.to_bytes()}")
            return False
        
        # Got an ACK
        log_debug("Got ACK")
        return True

    def get_message(self, port: Serial):
        log_debug("Receiving message")

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

        # Magic byte received, create a new message instance
        log_debug("Got magic byte")
        ans = Message()
        ans.magic = MESSAGE_MAGIC

        # Read header
        header = port.read(5)
        if len(header) != 5:
            log_error("Failed to read message header from module: Timeout")
            return None
        ans.type = header[0]
        ans.src = header[1]
        ans.dst = header[2]
        ans.len = header[4]*256 + header[3]
        log_debug(f"Got header: {ans.to_bytes().hex()}")
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
    
    def send_image_new(self, module_nr: int):
        message = Message(MESSAGE_TYPE_IMG_NEW)
        return self.send_message_module(module_nr, message)

    def send_image_append(self, module_nr: int, img_data: np.array):
        # Flipping the image, if required, cannot be done in this function. It
        # only takes blocks of 256 bytes, which is not a multiple of 45*3, which
        # means that flipping the image may require bytes from the past/next
        # call to this function.
        module = self.module_port_addr_mirror[module_nr]
        message = Message(MESSAGE_TYPE_IMG_APP, img_data)
        return self.send_message_module(module_nr, message)


class ModuleController(Thread):
    def __init__(self, config, command_queue):
        Thread.__init__(self, daemon=True)
        self.command_queue = command_queue
        self.router = PacketRouter(config["port_up"], config["port_down"], config["baudrate"])
        self.module_cnt = self.router.get_num_modules()
        self.height = self.module_cnt*45
        self.width = 0
        self.uploading_image = False
        self.playing = False
        self.image = Image.open("image.png")
        self.progress_extra_steps = 0
        self.avrctrl = AvrCtrl(config["avr_spi_bus"], config["avr_spi_device"])

        # Set up GPIOs
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(0, GPIO.IN)

        log_info(f"Found {self.module_cnt} modules with {self.height} pixels")

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

    # This is a separate thread doing all the time-intensive tasks, like scaling the image
    # or uploading it to the modules.
    def run(self):
        command_queue_internal = Queue()
        last_trigger = True
        while True:
            time.sleep(0.1)
            # TODO: Check shutdown pin (maybe not here, this loop blocks until a new command is available)
            # Check if trigger button is pushed
            new_trigger = GPIO.input(0)
            if not new_trigger and last_trigger: # Detect falling edge of button trigger line
                command_queue_internal.put({"command": "trigger"})
            last_trigger = new_trigger

            # Move stuff from command_queue to command_queue_internal
            while not self.command_queue.empty():
                command_queue_internal.put(self.command_queue.get())

            # Process messages
            if not command_queue_internal.empty():
                command_data = command_queue_internal.get()
                log_debug(f"Processing command: {command_data['command']}")
                if command_data["command"] == "init_modules":
                    # Send a reset command
                    self.router.find_modules()
                    # TODO: We need to update module_cnt and height - maybe also trigger an image upload
                    # TODO: Calling this command will currently do bad things if the arrangement of the
                    # TODO: modules changed.
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
                    self.image_scaled = self.image.convert('RGB', matrix)
                    log_debug(f"Applied color temperature of {temp_sel} K")

                    # Apply brightness correction
                    enhancer = ImageEnhance.Brightness(self.image_scaled)
                    log_debug(f"Brightness: {self.led_settings['brightness']}")
                    self.image_scaled = enhancer.enhance(self.led_settings["brightness"])
                    log_debug(f"Applied brightness of {self.led_settings['brightness']*100}%")

                    # TODO: Crop image if required

                    # Scale image
                    # TODO: Only if it has to be rescaled...
                    self.width = round(self.height*self.image.size[0]/self.image.size[1])
                    log_debug(f"Scaling image to {self.width}x{self.height}")
                    self.image_scaled = self.image_scaled.resize((self.width, self.height))
                    log_debug(f"Image resized to {self.width}x{self.height}")

                    # Mirror image
                    if self.led_settings["mirror"]:
                        self.image_scaled = ImageOps.mirror(self.image_scaled)

                    # Save scaled image
                    self.image_scaled.save("image_scaled.png")

                    # Calculate the hash of the scaled image
                    image_bytes = self.image_scaled.tobytes()
                    self.led_settings["image_hash"] = hashlib.sha256(image_bytes).hexdigest()
                    log_debug(f"New image hash: {self.led_settings['image_hash']}")
                    log_info("Processed and saved new image")
                elif command_data["command"] == "upload_image":
                    log_info("Uploading new image")
                    self.uploading_image = True
                    self.update_progress("processing", "Uploading image", 0.0)

                    width = self.image_scaled.size[0]
                    height = self.image_scaled.size[1]
                    if height != self.height:
                        # This should hopefully never happen...
                        log_error(f"Cannot upload image: size of scaled image does not match hardware configuration!")
                        log_error(f"Scaled image height: {height}, hardware height: {self.height}")
                        break
                    log_debug(f"Image size: {width}x{height}")

                    # Split the image for the modules
                    module_data = []
                    for mid in range(self.module_cnt):
                        cut_image = self.image_scaled.crop((0, mid*45, width, (mid+1)*45))
                        # Swap the colors to the right order
                        r,g,b = cut_image.split()
                        cut_image = Image.merge("RGB", (g, r, b))
                        # Flip the image, if required
                        if self.router.module_port_addr_mirror[mid]["mirror"]:
                            cut_image = cut_image.transpose(Image.FLIP_TOP_BOTTOM)
                        # Transpose image (we want data along columns) and convert to numpy uint8 array
                        cut_data = cut_image.transpose(Image.TRANSPOSE).tobytes()
                        module_data.append(cut_data)

                    # Send the image to the modules in packets of 256 bytes
                    # TODO: This can probably be optimized by sending data to all modules at once
                    # TODO: and then wait for the ACKs. But this would require some rework in the
                    # TODO: ACK management.
                    num_packets = math.ceil(len(module_data[mid])/256)
                    for mid in range(len(module_data)):
                        # Start a new image for that module
                        log_info(f"Sending image data to module {mid}")
                        if not self.router.send_image_new(mid):
                            log_error(f"Unable to send new image command to module {mid}")
                        for bid in range(num_packets):
                            # Cut the data, convert it to numpy and send it to the module
                            data_cut = module_data[mid][bid*256:(bid+1)*256]
                            data_cut = np.frombuffer(data_cut, dtype=np.uint8)
                            if not self.router.send_image_append(mid, data_cut):
                                log_error(f"Unable to send image data to module {mid}")
                                break
                            progress = (mid*num_packets + bid + 1)/(num_packets*len(module_data))
                            log_debug(f"Uploading image... {progress*100:.0f} %")
                            self.led_settings["progress_value"] = progress
                            if not self.uploading_image:
                                log_info("Cancelled upload")
                                self.update_progress("noimage", "", 0.0)
                                break
                    self.update_progress("ready", "", 0.0)
                    log_info("Upload done")

                    # Set the current image width as trigger count for the main AVR
                    self.avrctrl.set_trigger_count(width)
                elif command_data["command"] == "set_speed":
                    # We want 5.5 mm per LED, the period needs to be in microseconds per column
                    period = int(5.5e-3/self.led_settings['speed']*1e6)
                    if period > 65565:
                        period = 65565
                    self.avrctrl.set_period(period)
                    self.avrctrl.set_on_time(int(period/2))  # TODO: Maybe we want to choose a different duty cycle here
                    log_info(f"Set speed to {self.led_settings['speed']} m/s, {period} µs/column")
                elif command_data["command"] == "set_repeat":
                    self.avrctrl.set_infinite_repeat(self.led_settings['repeat'])
                    log_info(f"Sent repeat value of {self.led_settings['repeat']} to modules")
                elif command_data["command"] == "set_pixel_mode":
                    for mid in range(len(module_data)):
                        if not self.router.send_pixel_mode(mid, self.led_settings['pixel_mode']):
                            log_error(f"Unable to send new pixel mode to module {mid}")
                    log_info(f"Sent pixel_mode value of {self.led_settings['pixel_mode']} to modules")
                elif command_data["command"] == "trigger":
                    self.led_settings["progress_status"] = "playing"
                    self.led_settings["progress_value"] = 0.0
                    self.playing = True

                    # Wait the trigger delay, while updating the progress values
                    delay = self.led_settings['trigger_delay']
                    log_info(f"Got trigger command, will sleep {delay} s")
                    slept = 0.0
                    while slept < delay:
                        time.sleep(0.05)
                        slept += 0.05
                        self.led_settings["progress_value"] = slept/delay
                        if not self.playing:
                            self.led_settings["progress_status"] = "ready"
                            break

                    # TODO: Send trigger to microcontroller on main board
                    # TODO: Find something how we can know the current state without estimating it.
                    # TODO: Probably the µC on the host board can tell us the current state using its serial wire.
                    self.led_settings["progress_value"] = 0.0
                    self.led_settings["progress_status"] = "playing"
                    for mid in range(len(module_data)):
                        if not self.router.send_prep(mid):
                            log_error(f"Unable to send prepare message to module {mid}")
                    self.avrctrl.start_trigger()
                    log_info("Trigger sent")

                    # TODO: This is just for debug purposes: Send trigger directly to modules with 1s delay between each trigger
                    """log_info(f"Will trigger {self.width} times")
                    self.led_settings["progress_value"] = 0.0
                    if not self.router.send_prep(0):
                        log_error("Unable to send prepare message")
                    time.sleep(1)
                    for column in range(self.width):
                        if not self.router.send_trig(0):
                            log_error("Unable to send trigger message")
                        log_info(f"Triggered")
                        time.sleep(1)
                    self.led_settings["progress_value"] = 0.0
                    self.led_settings["progress_status"] = "ready"
                    log_info(f"Playback done")"""

                    # Update the state
                    while self.playing is True:
                        # TODO: Once playback is done, we need to tell the modules to turn off the LEDs
                        # Update the state
                        timer_counter = self.avrctrl.get_timer_counter()
                        self.led_settings["progress_value"] = timer_counter/self.image_scaled.size[0]
                        if timer_counter == 0:  # TODO: This is not sufficient, if we are playing continously this might be 0 sometimes - we should have a flag for "done"
                            break
                    log_info("Play done")
                    self.led_settings["progress_value"] = 0.0
                    self.led_settings["progress_status"] = "ready"
                    self.playing = False
                    self.avrctrl.stop_trigger() # Make sure the trigger is stopped, for example if the user requested the stop
                    self.router.send_reset_leds() # Turn off all LEDs

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
        # TODO: This method is not perfect: If there are a lot of upload commands in a row it may happen that the image is uploaded multiple times
        if self.uploading_image:
            self.uploading_image = False
        # Add the image upload to the command queue - asynchronously
        self.command_queue.put({"command": "upload_image"})

    def set_speed(self, speed):
        self.led_settings["speed"] = speed
        self.command_queue.put({"command": "set_speed"})

    def set_brightness(self, brightness):
        log_debug(f"Setting brightness to {brightness}")
        self.led_settings["brightness"] = brightness
        # Update the image
        self.update_image()
    
    def set_color_temperature(self, color_temperature):
        log_debug(f"Setting color temperature to {color_temperature} K")
        self.led_settings["color_temperature"] = color_temperature
        # Update the image
        self.update_image()

    def set_trigger_delay(self, trigger_delay):
        log_debug(f"Setting trigger delay to {trigger_delay} s")
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
    config["avr_spi_bus"] = int(cfgparser.get("blinkybar", "avr_spi_bus"))
    config["avr_spi_device"] = int(cfgparser.get("blinkybar", "avr_spi_device"))

    log_info("Started BlinkyBar Server")

    static_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')
    conf = {
        '/': {
            'tools.staticdir.root': static_dir,
            'tools.staticdir.on': True,
            'tools.staticdir.dir': '',
        }
    }
    cherrypy.config.update({'server.socket_host': '192.168.178.60'})
    cherrypy.quickstart(WebServer(config), '/', conf)
