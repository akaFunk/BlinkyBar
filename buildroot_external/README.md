# Buildroot config
You need a Linux on the Raspberry Pi Zero with some custom configuration (including device-tree stuff). This folder includes the files required to make a custom buildroot build. This custom embedded Linux has a few advantages:
- The image only includes what is really needed. This will decrease the size of the image substantially (currently we need less than 100 MB) and it also improves the boot time (currently we need ~5 seconds).
- The image contains multiple partitions. The boot and system partition are mounted read only (including noatime). The data partition contains the current configuration. It is mounted rw only when required. This reduces wear of the SD card and the risk of a damaged it when the Pi is turned off without a proper shutdown.
- We need a custom device tree to enable the SPI to UART converter, which can be easily integrated into the buildroot system.
Nevertheless, it is possible to use the standard RaspiOS with the mentioned downsides. A tutorial how to set it up is given below.

## How to build

```bash
git clone git://git.busybox.net/buildroot
cd buildroot
git checkout 2021.02
make BR2_EXTERNAL=../path/to/repo/buildroot_external/ BlinkyBar_defconfig
make
```

Das SD-Karten-Image liegt im Buildrootordner unter output/images/sdcard.img.

## Using Raspberry Pi OS
Here is a step-by-step guide on how to set up a RaspiOS for the BlinkyBar. It is also helpful if you want to learn what we have done to the buildroot to get everything up and running.

### Connecting to the Pi
The system is a so-called headless-system. You don't have (need) a monitor or keyboard. To get access to the Pi there are several options. The easiest one is to use Wifi and SSH. We will first tell the Pi to connect to your local Wifi network and enable SSH. Later, we will reconfigure the Pi to provide an access point. This has to be done later, as we will need to download some stuff.

Flash the Raspberry Pi OS image to an SD card. After that open the boot partition and create a file called `ssh`, which will tell the Pi to enable the ssh server upon first boot. Then create a second file called `wpa_supplicant.conf` with the following content:
```text
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="SSID"
    psk="PASSWORD"
}
```
Replace `SSID` with your network name, keep the quotes. Also set the password. You may also want to change the country, which will influence what frequencies the Pi is allowed to use due to different regulatory rules in different countries.

Plug the SD card into the Pi and power it on by pressing the power button for at least 2 seconds. Now open the configuration site of your local Wifi router and find out the IP address of the Pi, connect to it using ssh:
```sh
$ ssh pi@IPADDRESS
```
The default password is `raspberry`.

### Device tree configuration
We need a custom device tree configuration to enable support for SPI1 and the SC16IS752 SPI to dual-UART converter. Add the following lines to `/boot/config.txt` at the very bottom:
```text
dtoverlay=spi1-1cs
dtoverlay=sc16is752-spi0,int_pin=24,xtal=16000000
```
The first line enables SPI1 with one chip-select (GPIO18). SPI1.0 is used as the interface to the AVR on the main PCB. The Pi will send commands to the AVR controlling the trigger signal, including its speed and when to turn on/off. The second line enables the SC16IS752 driver on SPI0 with GPIO24 as the interrupt pin and an external crystal of 16 MHz, which will allow the baud rates 500k and 1M.

After a reboot, make sure you have the SPI1 interface at `/dev/spidev1.0` and the two serial interfaces at `/dev/ttySC0` and `/dev/ttySC1`.

### Serial terminal
As the Wifi will be used for the access point, it may be handy to use a serial terminal for initial communication. To enable the serial terminal, add the line
```
enable_uart=1
```
to `/boot/config.txt`. Also make sure you have the following parameters in `/boot/cmdline.txt`:
```
console=serial0,115200 console=tty1
```
Then connect a USB to serial converter (like FTDI FT232R) to the main module. The RX/TX signals are on the debug header and labeled `PI_TXD` and `PI_RXD`. Make sure to connect RX to TX and vice versa. The names on the BlinkyBar PCB refer to the Pi side.

Then run a serial terminal software like HyperTerminal (Windows) or minicom (Linux) with 115200 baud:
```
minicom -D /dev/ttyUSB2 -b 115200
```

### Dependencies
You need to install a few things before you can start the BlinkyBar main application:
```sh
$ sudo apt install python3-pip libopenjp2-7V python3-numpy python3-rpi.gpio
$ pip3 install cherrypy pillow ujson pyserial
```
Make sure the install the stuff using pip3 with the user which will also run the blinkybar.py server.

Note: numpy is not installed through pip, as we experienced an issue with libcblas.so.3. Raspberry Pi OS puts the symbols into libblas.so and numpy needs to be linked against this library, which is not the case for the current PyPi version.

### BlinkyBar Server
TODO

### Autostart
TODO

### Wifi access point
The Pi will generate a Wifi access point. You connect to it and open the website provided by the BlinkyBar server.

TODO

### Read-Only mode
You can put the Raspberry Pi in a secure read-only mode after you configured everything. To do that run
```sh
$ sudo raspi-config
```
Navigate to `Performance Options` and `Overlay File System`. Enable the overlay file system and make the boot partition write-protected. This will prevent any write to the SD card, making the system much more reliable. But note: Although it is possible to changes files in the filesystem (changes will be stored in the RAM overlay), after a reboot everything is back to the point when you enabled it overlay. So the BlinkyBar will forget its last image and any configuration changes.
