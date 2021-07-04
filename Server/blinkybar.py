import logging
import cherrypy
import os
from PIL import Image, ImageEnhance
import ujson
import io
import serial
from threading import Thread
import time
from queue import Queue
import datetime
import hashlib
#import configparser

cherrypy._cplogging.LogManager.time = lambda self : \
     datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:23]

# State
led_settings = {
    "status": "ok",
    "brightness": 0.5,
    "speed": 0.5,
    "trigger_delay": 1.0,
    "allow_scaling": True,
    "image_hash": "01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b",
    "msg": ""
}

class Controller(Thread):
    def __init__(self, command_queue):
        Thread.__init__(self, daemon=True)
        self.command_queue = command_queue
        self.uploading_image = False
        self.height = 120 # TODO: This should come from the stick

    def run(self):
        while True:
            command_data = self.command_queue.get()
            cherrypy.log("Got command: " + command_data["command"])
            if command_data["command"] == "upload_image":
                self.uploading_image = True
                for k in range(10):
                    cherrypy.log(f"Uploading image... {k+1}/10")
                    time.sleep(1)
                    if not self.uploading_image:
                        cherrypy.log("Cancelling upload")
                        break
            elif command_data["command"] == "set_speed":
                cherrypy.log("Setting speed...")
            elif command_data["command"] == "trigger":
                cherrypy.log(f"Trigger in {command_data['delay']} seconds")
            elif command_data["command"] == "set_speed":
                cherrypy.log(f"Set speed to {command_data['speed']} m/s")
            elif command_data["command"] == "update_image":
                cherrypy.log("Processing new image")

                # Save new original image as png
                # The compression level is chosen fairly low to speed things up
                self.image.save("image.png", compress_level=1)
                cherrypy.log("Saved original image")

                # Apply brightness correction .filter?
                enhancer = ImageEnhance.Brightness(self.image)
                self.image = enhancer.enhance(led_settings["brightness"])
                cherrypy.log(f"Applied brightness of {led_settings['brightness']*100}%")

                # TODO: Crop image if required

                # Scale image
                # TODO: Only if it has to be rescaled...
                width = round(self.height*self.image.size[0]/self.image.size[1])
                image_scaled = self.image.resize((width, self.height))
                cherrypy.log(f"Image resized to {width}x{self.height}")

                # Save scaled image
                image_scaled.save("image_scaled.png")
                cherrypy.log("Saved scaled image")

                # Calculate the hash of the scaled image
                image_bytes = self.image.tobytes()
                led_settings["image_hash"] = hashlib.sha256(image_bytes).hexdigest()
                cherrypy.log("Updated scaled image hash")

    def new_image(self, new_image):
        # Save the new image
        self.image = new_image
        # Trigger an image update and uplload
        self.update_image()

    def update_image(self):
        # Add the command to the queue
        self.command_queue.put({"command": "update_image"})
        # Trigger an image upload
        self.upload_image()

    def upload_image(self):
        # Cancel a currently running upload
        # TODO: This method is not perfect, if there are a lot of upload commands in a row
        if self.uploading_image:
            self.uploading_image = False
        # Add the image upload to the command queue
        self.command_queue.put({"command": "upload_image"})

    def set_speed(self, speed):
        self.command_queue.put({
            "command": "set_speed",
            "speed": speed
        })
    
    def trigger(self, delay):
        self.command_queue.put({
            "command": "trigger",
            "delay": delay
        })


class WebServer(object):
    def __init__(self):
        self.command_queue = Queue()
        self.controller = Controller(self.command_queue)
        self.controller.start()
        cherrypy.log("BlinkyBar server started")

    # Load index.html
    @cherrypy.expose
    def index(self):
        return open(os.path.join(static_dir, "index.html"))

    # Get settings object
    @cherrypy.expose
    def get_settings(self):
        return ujson.dumps(led_settings, indent = 4)
    
    @cherrypy.expose
    def settings(self, speed=None, brightness=None, trigger_delay=None, allow_scaling=None):
        # Check all the variables first
        if speed is not None:
            try:
                speed = float(speed)
            except ValueError:
                led_settings.update(dict({"status:": "error", "msg": "Speed is not a float"}))
                return ujson.dumps(led_settings)
            if speed < 0.1 or speed > 100:
                led_settings.update(dict({"status:": "error", "msg": "Speed is out of range"}))
                return ujson.dumps(led_settings)
        if brightness is not None:
            try:
                brightness = float(brightness)
            except ValueError:
                led_settings.update(dict({"status:": "error", "msg": "Brightness is not a float"}))
                return ujson.dumps(led_settings)
            if brightness < 0.1 or brightness > 1.0:
                led_settings.update(dict({"status:": "error", "msg": "Brightness is out of range"}))
                return ujson.dumps(led_settings)
        if trigger_delay is not None:
            try:
                trigger_delay = float(trigger_delay)
            except ValueError:
                led_settings.update(dict({"status:": "error", "msg": "Trigger delay is not a float"}))
                return ujson.dumps(led_settings)
            if trigger_delay < 0 or trigger_delay > 1000.0:
                led_settings.update(dict({"status:": "error", "msg": "Trigger delay is out of range"}))
                return ujson.dumps(led_settings)
        if allow_scaling is not None:
            if allow_scaling.lower() in ['true', '1',]:
                allow_scaling = True
            elif allow_scaling.lower() in ['false', '0',]:
                allow_scaling = False
            else:
                led_settings.update(dict({"status:": "error", "msg": "Allow scaling delay is out of range"}))
                return ujson.dumps(led_settings)

        # All values seem to be ok, update the state
        if speed is not None:
            led_settings["speed"] = speed
            # Trigger an update to the modules
            self.controller.set_speed(led_settings["speed"])
        
        if brightness is not None:
            led_settings["brightness"] = brightness
            # TODO: Trigger an image update
        
        if trigger_delay is not None:
            led_settings["trigger_delay"] = trigger_delay
        
        if allow_scaling is not None:
            led_settings["allow_scaling"] = allow_scaling
            # TODO: Trigger an image update

        led_settings.update(dict({"status:": "ok", "msg": ""}))
        return ujson.dumps(led_settings)

    @cherrypy.expose
    def status(self):
        # TODO: Implement actual status
        return ujson.dumps({"progress": 0.7, "msg": "Uploading to modules"})

    # Upload an image as png/jpg/gif/... in post data
    @cherrypy.expose
    def set_image(self, image_obj):
        cherrypy.log("Got a new image")
        image_data = image_obj.file.read()

        cherrypy.log("set_image data read")
        new_image = Image.open(io.BytesIO(image_data))
        self.controller.new_image(new_image)
        cherrypy.log("set_image processed")
        return ujson.dumps({"status": "ok"})
    
    # Download the full image
    @cherrypy.expose
    def get_image(self):
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "image.png")
        return cherrypy.lib.static.serve_file(path, "image/png", "image.png")
    
    # Download the scaled image
    @cherrypy.expose
    def get_image_scaled(self):
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "image_scaled.png")
        return cherrypy.lib.static.serve_file(path, "image/png", "image_scaled.png")
    

if __name__ == '__main__':
    #config = configparser.RawConfigParser()
    #config.read("BlinkyBar.conf")
    #print(config.get("general", "test"))

    cherrypy.log("Started BlinkyBar Server")

    static_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')
    conf = {
        '/': {
            'tools.staticdir.root': static_dir,
            'tools.staticdir.on': True,
            'tools.staticdir.dir': ''
        }
    }
    cherrypy.quickstart(WebServer(), '/', conf)
