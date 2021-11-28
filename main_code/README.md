# Main PCB AVR code
This folder contains the code for the AVR on the main PCB. The purpose of this controller is battery monitoring, power management, and generation of the trigger signal for the modules.

Once the controller turns on by pushing the button connected to the `MASTER_ON` signal, it is responsible to set `PWR_EN` high to keep the power supply turned on. If the battery voltage is too low, the AVR will turn off the power supply by driving the `PWR_EN` line low. This will also turn off the power of the AVR itself. Before that it will notify the Pi, so the Pi can shut down the modules as they will not be needed if the main module has no power.

The AVR talks to the Raspberry Pi using an SPI. On the Pi side the SPI1 is used in master mode, which needs to be activated using an additional overlay. See the readme file in `buildroot_external` folder for details on that. The AVR uses its only internal hardware SPI, which is shared with the `ISP` interface for promming the AVR. The two 330 Ohm resistors `R7` and `R8` make sure that there are no collisions while debugging and the `ISP` interface is the primary one. The AVR runs at 8 MHz. 16 MHz is not possible, as the supply voltage is only 3.3V.

The Pi will set the period and on time of the trigger signal, how many colums there are and it will start/stop the trigger signal.

## SPI protocoll
The SPI clock should be fairly low, to make sure that the AVR can keep up. Don't know the exact value, 10 kHz works.

The protocoll is a single packet of 5 bytes in both directions. These 5 bytes have to be encapsulated in a single chip-select sequence. The packet from the Pi to the AVR contains the following data, all values are little endian:

| Bytes | Meaning |
|---|---|
| 1 | Command flags: <br> bit 0: start trigger<br>bit 1: stop trigger <br> bit 2: infinite repeat <br> If nothing is set, the Pi only wants to read the voltage/timer_counter and no action is carried out and the local state is not altered. |
| 2 | Period of the trigger signal, given in µs |
| 2 | On-time of the trigger signal, given in µs |
| 2 | Trigger count, number of negative pulses on the trigger line |

And the answer, which is returned in each request contains the following information:

| Bytes | Meaning |
|---|---|
| 1 | Dummy, always 0 |
| 2 | Battery voltage, given in mV |
| 2 | Current timer counter value of the current progress, which counts from 0 to the period value minus 1 |
| 1 | Shutdown request, 1 if the power button was pressed or the battery voltage is too low, otherwise 0 |
| 1 | Dummy, always 0 |

TODO: Add a automatic shutdown if we have not heard from the Pi in a while. This would also be helpfull for the modules.
