# LEDStrip Server
The server is small Python script running on the main module's Raspberry PI Zero W. The Pi provides a Wifi access point. Once connected, the server is reachable under http://192.168.138.1. The server provides the necesarry website and API to control the LEDStrip. This includes uploading images, setting the speed, brightness, trigger delay, and a few other options. It also allows to trigger the LEDStrip, additionally to the hardware button on the LEDStrip itself.

## API
The server is written in Python 3 and based on [bottle.py](bottlepy.org), which provides a simple webserver and integrates easily into python. Each set-query to the API will return a JSON string containing two things: A status variable, which is either "ok" or "error" and an optional "msg" string, containing a message which will be shown to the user.

The API provides the following endpoints:

### /set/brightness/\<value\>
Set the brightness value of the LEDStrip. The value can be between 0 and 1 as a floating point number. Settings this value will trigger an upload of the image to the modules. The default value is 1.

Here is an example: http://192.168.138.1/set/brightness/0.65

### /set/speed/\<value\>
Set the speed of the image playback. The value is given in milliseconds and floating point values between 1 and 1000 are allowed. The time describes the time between two column updates. The default value is 0.5.

Here is an example: http://192.168.138.1/set/speed/7.5

### /set/trigger_delay/\<value\>
Set the delay between pressing the trigger button and starting the playback of the image. The value is given in seconds and any positive floating points value is allowed. The default value is 0.

Here is an example: http://192.168.138.1/set/trigger_delay/1.0

### /set/allow_scaling/\<value\>
Defines if the LEDStrip is allowed to scale the image or not. This allows to prepare pixel-precise images. Note that if the image height is exactly the same as the number of available pixels, the LEDStrip will not scale the image as well. If scaling is not allowed and the image is smaller than the current LEDStrip configuration, only the upper pixels will be used. If no scaling is allowed and the image is larger, the image will be cut at the bottom. Accepted values are true or false. A change of this value might trigger an image upload, if the result will be different. The default value is true.

Here is an example: http://192.168.138.1/set/allow_scaling/false


### /set/image
Upload an image to the LEDStrip. The image has to be attached in the POST data. A new image will trigger an image upload to the modules.

TODO: A detailed description to follow, once implemented ;)

Here is an example: http://192.168.138.1/set/image + POST data

### /get/settings
Read all settings as a JSON string, which has this structure:
```json
{
    "brightness": 0.5,
    "speed": 0.5,
    "trigger_delay": 1.0,
    "allow_scaling": true
}
```
Here is an example: http://192.168.138.1/get/settings

### /get/image
Returns the currently stored image. The server internally converts the image to a PNG file on upload and this is what you will get here.

Here is an example: http://192.168.138.1/get/image

## Website
The website is delivered by the server to the webbrowser and provides the GUI for the LEDStrip. The application is based on [Vue.js](https://vuejs.org/), version 3.

TODO: A detailed description to follow, once implemented ;)

TODO: Screenshots
