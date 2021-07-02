# https://docs.cherrypy.org/en/latest/tutorials.html#tutorials

import cherrypy
import os
from PIL import Image
import ujson
import io
import serial
from threading import Thread
import time
from queue import Queue

# State
led_settings = dict()
led_settings["brightness"] = 0.5
led_settings["speed"] = 0.5
led_settings["trigger_delay"] = 1.0
led_settings["allow_scaling"] = True


class Controller(Thread):
    def __init__(self, command_queue):
        Thread.__init__(self, daemon=True)
        self.command_queue = command_queue
        self.uploading_image = False
        print("Hello from thread init")

    def run(self):
        while True:
            data = self.command_queue.get()
            print("Got command: " + data["command"])
            if data["command"] == "upload_image":
                self.uploading_image = True
                for k in range(10):
                    print(f"Uploading image... {k+1}/10")
                    time.sleep(1)
                    if not self.uploading_image:
                        print("Cancelling upload")
                        break
            elif data["command"] == "set_speed":
                print("Setting speed...")
            elif data["command"] == "trigger":
                print(f"Trigger in {data['delay']} seconds")
            elif data["command"] == "set_speed":
                print(f"Set speed to {data['speed']} m/s")

    def upload_image(self, image_data):
        # Cancel a currently running upload
        if self.uploading_image:
            self.uploading_image = False
        # Add the image upload to the command queue
        self.command_queue.put({
            "command": "upload_image",
            "iamge": image_data
        })

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
        print("Web server started")
        time.sleep(3)
        print("Adding image...")
        self.controller.upload_image("image data")
        time.sleep(3)
        print("Adding another image...")
        self.controller.upload_image("anotherimage data")
        time.sleep(12)

    # Load index.html
    @cherrypy.expose
    def index(self):
        return open(os.path.join(static_dir, "index.html"))

    # Get settings object
    @cherrypy.expose
    def get_settings(self):
        return ujson.dumps(led_settings, indent = 4)
    
    # Settings - brightness
    @cherrypy.expose
    def brightness(self, value=None):
        if value is not None:
            try:
                led_settings["brightness"] = float(value)
            except ValueError:
                return ujson.dumps({"status:": "error", "msg": "Value not a float"})
        return ujson.dumps({
            "status": "ok",
            "brightness": str(led_settings["brightness"])
        })

    # Settings - speed
    @cherrypy.expose
    def speed(self, value=None):
        if value is not None:
            try:
                led_settings["speed"] = float(value)
            except ValueError:
                return ujson.dumps({"status:": "error", "msg": "Value not a float"})
        return ujson.dumps({
            "status": "ok",
            "speed": str(led_settings["speed"])
        })

    # Settings - trigger_delay
    @cherrypy.expose
    def trigger_delay(self, value=None):
        if value is not None:
            try:
                led_settings["trigger_delay"] = float(value)
            except ValueError:
                return ujson.dumps({"status:": "error", "msg": "Value not a float"})
        return ujson.dumps({
            "status": "ok",
            "trigger_delay": str(led_settings["trigger_delay"])
        })

    # Settings - allow_scaling
    @cherrypy.expose
    def allow_scaling(self, value=None):
        if value is not None:
            if value.lower() in ['true', '1',]:
                led_settings["allow_scaling"] = True
            elif value.lower() in ['false', '0',]:
                led_settings["allow_scaling"] = False
            else:
                return ujson.dumps({
                    "status:": "error",
                    "msg": "Value not a bool"
                })
        return ujson.dumps({
            "status": "ok",
            "allow_scaling": str(led_settings["allow_scaling"])
        })

    # Upload an image as png/jpg/gif/... in post data
    @cherrypy.expose
    def set_image(self):
        # Get post data
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        #print(rawbody)
        #return "Done"
        image = Image.open(io.BytesIO(rawbody))
        image.save("image.png")
        image.show()
    
    # Upload an image as png/jpg/gif/... in post data
    @cherrypy.expose
    def get_image(self):
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "image.png")
        return cherrypy.lib.static.serve_file(path, "image/png", "image.png")
    

if __name__ == '__main__':
    static_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')

    conf = {
        '/': {
            'tools.staticdir.root': static_dir,
            'tools.staticdir.on': True,
            'tools.staticdir.dir': ''
        }
    }

    cherrypy.quickstart(WebServer(), '/', conf)



#        # Get post data
#        cl = int(cherrypy.request.headers['Content-Length'])
#        rawbody = cherrypy.request.body.read(int(cl))
#        print("Data: \"" +  rawbody.decode("utf-8") + "\"")
#        print("Length: " + str(cl))
#        if cl == 0:
#            return "here are the settings..."
#        else:
#            return "Done"