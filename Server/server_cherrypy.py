# https://docs.cherrypy.org/en/latest/tutorials.html#tutorials

import cherrypy
import os
import PIL as pil
import ujson

led_settings = dict()
led_settings["brightness"] = 0.5
led_settings["speed"] = 0.5
led_settings["trigger_delay"] = 1.0
led_settings["allow_scaling"] = True

class Server(object):
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

    # Upload an image as png/jpg/gif/... in post data
    @cherrypy.expose
    def image(self):
        # Get post data
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        print(rawbody)
        return "Done"
    

if __name__ == '__main__':
    static_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')

    conf = {
        '/': {
            'tools.staticdir.root': static_dir,
            'tools.staticdir.on': True,
            'tools.staticdir.dir': ''
        }
    }

    cherrypy.quickstart(Server(), '/', conf)



#        # Get post data
#        cl = int(cherrypy.request.headers['Content-Length'])
#        rawbody = cherrypy.request.body.read(int(cl))
#        print("Data: \"" +  rawbody.decode("utf-8") + "\"")
#        print("Length: " + str(cl))
#        if cl == 0:
#            return "here are the settings..."
#        else:
#            return "Done"