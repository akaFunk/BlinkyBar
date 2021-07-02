# LEDStrip Server
The server is small Python script running on the main module's Raspberry PI Zero W. The Pi provides a Wifi access point. Once connected, the server is reachable under http://192.168.138.1. The server provides the necesarry website and API to control the LEDStrip. This includes uploading images, setting the speed, brightness, trigger delay, and a few other things. It also allows to trigger the LEDStrip, additionally to the hardware button on the LEDStrip itself.

## API
The server is written in Python 3 and based on [cherrypy](cherrypy.org), which provides a simple webserver and integrates easily into python. There are three different endpoints for the API:

### settings
Settings can take several parameters:

- **speed** is a floating point value between 0.1 and 10, given in meters per second. It defines the column playback speed of the image. The default value is 2.0.
- **brightness** is the brightness of the image as a floating point value between 0 and 1. Settings this value will trigger an upload of the image to the modules. The default value is 1.
- **trigger_delay** sets the delay between pressing the trigger button and starting the playback of the image. The value is given in seconds and any positive floating points value is allowed. The default value is 0.
- **allow_scaling** defines if the LEDStrip is allowed to scale the image or not. This allows to prepare pixel-precise images. Note that if the image height is exactly the same as the number of available pixels, the LEDStrip will not scale the image as well. If scaling is not allowed and the image is smaller than the current LEDStrip configuration, only the upper pixels will be used. If no scaling is allowed and the image is larger, the image will be cut at the bottom. Accepted values are true or false. A change of this value might trigger an image upload, if the result will be different. The default value is true.

All parameters are optional. A query looks, for example, like this:

http://192.168.138.1/settings?speed=1.0&allow_scaling=true

All queries will return a JSON string with the following structure:
```json
{
    "status": "ok",
    "brightness": 0.5,
    "speed": 2.0,
    "trigger_delay": 1.0,
    "allow_scaling": true,
    "msg": ""
}
```

The status variable is either "ok" or "error". For the latter one, the "msg" parameter contains an error message, which will be shown to the user.

### status
The status endpoint is a getter only. It returns a JSON string with the following structure:
```json
{
    "status": "processing",
    "progress": 0.7,
    "msg": "Uploading to modules"
}
```
The "status" may be any of "no image", "processing", or "ready". "no image" means that no image is available to be triggered, "processing" means that an uploaded image is currently being processed, and "ready" means that the uploaded image is ready to be triggered.
The "progress" is a float value between 0 and 1. It can be used to display a loading bar. The message in "msg" describes the current processing state, like "Converting image", "Uploading to modules", or similar. Both, "progress" and "msg" are only valid when "status" is "processing".


### set_image
Upload an image to the LEDStrip. The image has to be attached in the POST as a multipart/form-data object in the variable image_obj. A new image will trigger an image upload to the modules.

The endpoint is: http://192.168.138.1/set_image + POST data


### get_image
Returns the currently stored image. The server internally converts the image to a PNG file on upload and this is what you will get here.

Here is an example: http://192.168.138.1/get_image

### get_image_scaled
Returns the scaled version of the image, which is currently used for the LEDs. The image is of type PNG.

Here is an example: http://192.168.138.1/get_image_scaled

## Website
The website is delivered by the server to the webbrowser and provides the GUI for the LEDStrip. The application is based on [Vue.js](https://vuejs.org/), version 3.

TODO: A detailed description to follow, once implemented ;)

TODO: Screenshots
