from bottle import route, post, run, template, static_file, request
import os
import json
import cv2
import numpy as np

led_settings = dict()
led_settings["brightness"] = 0.5
led_settings["speed"] = 0.5
led_settings["trigger_delay"] = 1.0
led_settings["allow_scaling"] = True

@route('/get/settings')
def settings():
    print("Settings requested")
    return json.dumps(led_settings, indent = 4)

@route('/set/brightness/<value>')
def set_brightness(value):
    try:
        led_settings["brightness"] = float(value)
        return json.dumps({"status:": "ok"})
    except ValueError:
        return json.dumps({"status:": "error"})

@route('/set/speed/<value>')
def set_speed(value):
    try:
        led_settings["speed"] = float(value)
        return json.dumps({"status:": "ok"})
    except ValueError:
        return json.dumps({"status:": "error"})

@route('/set/trigger_delay/<value>')
def set_trigger_delay(value):
    try:
        led_settings["trigger_delay"] = float(value)
        return json.dumps({"status:": "ok"})
    except ValueError:
        return json.dumps({"status:": "error"})

@route('/set/allow_scaling/<value>')
def set_allow_scaling(value):
    if value.lower() in ['true', '1',]:
        led_settings["allow_scaling"] = True
        return json.dumps({"status:": "ok"})
    elif value.lower() in ['false', '0',]:
        led_settings["allow_scaling"] = False
        return json.dumps({"status:": "ok"})
    else:
        return json.dumps({"status:": "error"})

@post('/set/image')
def set_image():
    data = request.files.get('image')
    if data and data.file:
        img_data = data.file.read()
        filename = data.filename
        print(f"Got image {filename} with {len(img_data)} bytes")

        # Load image into OpenCV
        imp_np = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(imp_np, cv2.IMREAD_COLOR)

        # Save to disc as PNG
        if not cv2.imwrite("image.png", img):
            return json.dumps({"status:": "error", "msg": "Unable to save image to disk"})
        
        # TODO: Scale image

        # TODO: Start sending image to stick (async!)

        return json.dumps({"status:": "ok"})
    else:
        return json.dumps({"status:": "error", "msg": "No file provided"})

@route('/get/image')
def get_image():
    return static_file("image.png", os.path.dirname(os.path.realpath(__file__)))


@route('/')
def index():
    return static_file("index.html", os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static'))

run(host='localhost', port=8080, reloader=True)
