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

## Using RaspiOS
Here is a step-by-step guide on how to set up a RaspiOS for the BlinkyBar. It is also helpful if you want to learn what we have done to the buildroot to get everything up and running.

### Connecting to the Pi
TODO: Using serial line on debug pin header

### Device tree configuration
We need a custom device tree configuration to enable support for the SPI1 and the SC16IS752. Add the following lines to `/boot/config.txt`:
```text
dtoverlay=spi1-1cs
dtoverlay=sc16is752-spi0,int_pin=24,xtal=16000000
```
The first line enables SPI1 with one chip-select (GPIO18). SPI1.0 is used as the interface to the AVR on the main PCB. The Pi will send commands to the AVR controlling the trigger signal, including its speed and when to turn on/off. The second line enables the SC16IS752 driver on SPI0 with GPIO24 as the interrupt pin and an external crystal of 16 MHz, which will allow the baud rates 500k and 1M.

After a reboot, make sure you have the SPI1 interface at `/dev/spidev1.0` and the two serial interfaces at `/dev/ttySC0` and `/dev/ttySC1`.

### BlinkyBar Server
TODO

### Autostart
TODO

### Wifi
The Pi will generate a Wifi access point. You connect to it and open the website provided by the BlinkyBar server.

TODO

### Read-Only mode
You can put the Raspberry Pi in a secure read-only mode after you configured everything. To do that run
```sh
$ sudo raspi-config
```
Navigate to `Performance Options` and `Overlay File System`. Enable the overlay file system and make the boot partition write-protected. This will prevent any write to the SD card, making the system much more reliable. But note: Although it is possible to changes files in the filesystem (changes will be stored in the RAM overlay), after a reboot everything is back to the point when you enabled it overlay. So the BlinkyBar will forget its last image and any configuration changes.
