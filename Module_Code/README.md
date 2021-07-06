# Module Microcontroller Code
This folder contains the code for the microcontroller located on each module. This micro will receive the image data which will be used for the module's LEDs, save it into the flash memory and play it back once triggered.

The used microcontroller is an ATmega328p, which is the same as the one on the Arduino Uno. But we do not support the Arduino bootloader or using the Arduino IDE. This is a larger project and for that one should use proper tools.

## Building & Flashing
You need the avr-gcc and avr-binutils packages for building. Flashing requires avrdude and an external ISP prommer like the AVR ISP mkII, Atmel ICE, or similar.

To build the sources (there is also a pre-compiled hex file) type
```sh
$ make
```

After that you should modify the Makefile to fit your prommer. By default an AVR ISP mkII is expected. See
```sh
$ avrdude -c help
```
for a list of supported prommers. After doing that flash each module with:
```sh
$ make install
```
If you get some error message telling you that he was not able to access your prommer, your user probably doesn't have the right permission to access it. Use your favorite internet search engine to solve this problem, the keywords you are looking for are the name of your prommer, avrdude and udev (you need to add udev rules for it). If you are lazy, just run the install command with root privilegs.

## Bus System and Packets
A small recap of the hardware structure, for a detailed explanation of the hardware take a look at the folder ../Module_PCB.

The modules are daisy-chained through their UART. The TX of the host goes to the RX of the first module, the first module's TX goes to the second module's RX and so on. This is the downstream path.

There is also an upstream path. Each module can (software-controlled) bridge it's TX to the return path. The last module is the one which actually has to do this to get a closed daisy-chain.

Besides the daisy-chain there is the additional TRIGI/TRIGO signal. This signal comes from the microcontroller on the host. A rising edge on this signal signals the trigger for the output of the next column of the image.

The daisy-chained connection is used to transmit packets between the host and the modules. The packet's header contains information about the source and destination address, the type of the packet (i.e., a command), as well as the length of the data, and a few other things. The data follows the header and may have a length of up to 256 bytes and may also be of zero length.

If a packet's desination address is either the broadcast address or does not match the modules address, it is forwarded to the next module.

The big question is: How does a module determine its address? We decided against a hardware coding, as the modules would not be as modular - obviously. The host first sends a message to the broadcast address, telling every module to disable its uplink path and just transmit the packets to the next modules. In this configuration the host will not get any packets form the last module, as it will only forward them to the next module, which does not exist. This "return reset" message also causes all modules to set their address to 0. Next, the host will transmit a command to this address, containing a new unique address. The first module receives this message, sets its new address, enables the return path, acknowledges the reception, and disables the return path. This process is repeated until the host does not receive any answer. The last module that did answer will then get an extra message, telling it to enable its return path.

Here is the structure of the packet:
```c
typedef struct
{
    uint8_t magic;
    uint8_t type;
    uint8_t src;
    uint8_t dst;
    uint16_t len;
    uint8_t data[MESSAGE_MAX_DATA_SIZE];
} message_t;

```
with the following parameters:
- **magic** is a magic byte of value 0xab, which is always the first byte of a message. It is used to identify the start of a message in case of a loss of synchronization. Eventually a module will re-synchronize after a few packets.
- **type** is the type or command of the message.
- **src** is the the source address.
- **dst** is the destination address.
- **len** is the length of the data field as little endian.
- **data** is the data, which may have any length between 0 and 256.

The following message types are known:
- **MESSAGE_TYPE_RET_RST**: Reset the modules address, disable return path (RETO, ~RET_EN), always a broadcast message, len=0
- **MESSAGE_TYPE_ADDR**: Address idication for the module, len=1 (new address). The module will set the new address, enable the return path, send an ack message, and disable return path.
- **MESSAGE_TYPE_RET_SET**: Enable the module's return path (RETO, ~RET_EN), len=0.
- **MESSAGE_TYPE_PING**: Ping message, response with an ACK.
- **MESSAGE_TYPE_STAT**: Display a status value with the LEDs, len=1 (status vlaue).
- **MESSAGE_TYPE_DEL**: Delete the module's flash, len=0.
- **MESSAGE_TYPE_DATA**: Next data block for the module, len=1..256. The flash block size is 256 bytes and one column has 135 bytes per module.
- **MESSAGE_TYPE_PREP**: All data transmitted to modules, signal for the modules to prepare for trigger, len=0.
- **MESSAGE_TYPE_ACK**: ACK last message (also used as pong), len=0.
- **MESSAGE_TYPE_NACK**: NACK last message, len=0.

