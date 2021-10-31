# BlinkyBar Server

The server is small Python script running on the main module's Raspberry PI Zero W. The Pi provides a Wifi access point. Once connected, the server is reachable under http://192.168.138.1. The server provides the necesarry website and API to control the BlinkyBar. This includes uploading images, setting the speed, brightness, trigger delay, and a few other things. It also allows to trigger the BlinkyBar, additionally to the hardware button on the BlinkyBar itself.

## API

The server is written in Python 3 and based on [cherrypy](cherrypy.org), which provides a simple webserver and integrates easily into python. There are three different endpoints for the API:

### settings

Settings can take several parameters:

-   **speed** is a floating point value between 0.1 and 10, given in meters per second. It defines the column playback speed of the image. The default value is 2.0.
-   **brightness** is the brightness of the image as a floating point value between 0 and 1. Settings this value will trigger an upload of the image to the modules. The default value is 1.
-   **color_temperature** is the temperature of the surrounding light sources. The image is converted to reflect this color temperature. The default value, which makes (almost) no changes to the image is 6500 K. The valid range is between 1000 and 10000 K.
-   **trigger_delay** sets the delay between pressing the trigger button and starting the playback of the image. The value is given in seconds and any positive floating points value is allowed. The default value is 0.
-   **mirror** mirrors the image. A change will trigger an image upload.
-   **allow_scaling** defines if the BlinkyBar is allowed to scale the image or not. This allows to prepare pixel-precise images. Note that if the image height is exactly the same as the number of available pixels, the BlinkyBar will not scale the image as well. If scaling is not allowed and the image is smaller than the current BlinkyBar configuration, only the upper pixels will be used. If no scaling is allowed and the image is larger, the image will be cut at the bottom. Accepted values are true or false. A change of this value might trigger an image upload, if the result will be different. The default value is true.
-   **repeat** defines, if the image shall be repeated endlessly.
-   **pixel_mode** defines, if the playback should display pixels instead of hoizontal lines. If turned on, the modules will turn the LEDs on and off for each column with a durty cycle of 50 %, creating pixels in stead of horzontal lines.

All parameters are optional. A query looks, for example, like this:

http://192.168.138.1/settings?speed=1.0&allow_scaling=true

All queries will return a JSON string with the following structure:

```json
{
    "success": true,
    "error_msg": "",
    "brightness": 0.5,
    "speed": 0.5,
    "color_temperature": 6000,
    "trigger_delay": 1.0,
    "mirror": false,
    "allow_scaling": true,
    "repeat": false,
    "pixel_mode": true,
    "image_hash": "01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b",
    "progress_status": "noimage",
    "prograss_value": 0.0,
    "progress_msg": "",
    "system_error_msg": ""
}
```

If the "success" variable is false it indicates an error in the query. In that case the "error_msg" holds an error message.

Additionally the structure holds a few variables, indicating the state of the system:

-   **image_hash** contains the hash of the current scaled image, which can be used by the frontend to figure out if the image has changed since the last request. If that is the case, the frontend can ask for the new image.

-   **progress_status** may be any of "noimage", "processing", "ready", or "playing". "noimage" means that no image is available to be triggered, "processing" means that an uploaded image is currently being processed, "ready" means that the uploaded image is ready to be triggered, and "playing" means that the image is currently beeing played back. In the last case, a trigger will stop the playback.

-   **prograss_value** is a float value between 0 and 1. It can be used to display a loading bar while the an image is beeing processed or played. It is only valid if "progress_status" is either "processing" or "playing".

-   **progress_msg** contains a more detailed message about what is currently happening, especially during the image processing. It is only valid if "progress_status" is either "processing" or "playing".

-   **system_error_msg** may contain a system critical error message. If this string is not empty, the BlinkyBar will not function as expected and the message should be shown to the user.

### set_image

Upload an image to the BlinkyBar. The image has to be attached in the POST as a multipart/form-data object in the variable image_obj. A new image will trigger an image upload to the modules.

The endpoint is: http://192.168.138.1/set_image + POST data

### get_image

Returns the currently stored image. The server internally converts the image to a PNG file on upload and this is what you will get here.

Here is an example: http://192.168.138.1/get_image

### get_image_scaled

Returns the scaled version of the image, which is currently used for the LEDs. The image is of type PNG.

Here is an example: http://192.168.138.1/get_image_scaled

### Trigger

Triggers the image playback. If the playback is already running, it stops it. Can only be called if "progress_status" is "ready" or "playing".

## Website

The website is delivered by the server to the webbrowser and provides the GUI for the BlinkyBar. The application is based on [Vue.js](https://vuejs.org/), version 3.

TODO: A detailed description to follow, once implemented ;)

TODO: Screenshots
