# BlinkyBar
The BlinkyBar is a modular LED light painting device based on the WS2812B programmable RGB LEDs. It features modules with a length of approximately 250mm, which can be attached to a master module of an arbitrary length. The master module holds a Raspberry Pi Zero W, which provides access to the device with a Wifi access point. A website running on the Raspi allows to upload an image. Once the trigger button on the master module is pressed, the image is played back one column after another. Combining this with a long time expose will paint the uploaded image into thin air.

We are currently working on the first release. Images made with an earlier version are shown below. This older version featured only 60 LEDs per meter, while the new one will have 180 LEDs per meter.

## Images
Examples of the old version:
![Example Image 1](images/nyancat.jpg)
![Example Image 2](images/head.jpg)

3D rendering of the current main module:
![Example Image 1](images/blinkybar1_scaled.jpg)
![Example Image 1](images/blinkybar2_scaled.jpg)

## Building BlinkyBar

### Parts
Additional part required for a BlinkyBar with 4 modules and the main unit, i.e., 10 module PCBs and a length of 2475 mm and 450 LEDs.
For the PCBs you will find lists in CSV format exported from KiCad in each of the PCBs output folder.

| Description | Count | 3D Model |
|---|---|---|
| U-Profile, 30x20x2x495 mm (WxHxTxL), Aluminum | 1 | main_profile |
| U-Profile, 30x20x2x495 mm (WxHxTxL), Aluminum | 4 | module_profile |
| 6x6x100 mm, Steel | 8 | module_bolt |
| 3D-printed stand for the module PCB | 15 | module_stand |
| 3D-printed power button protector | 1 | main_button_protector |
| 3D-printed main case | 1 | main_case |
| 18650 Holder | 12 | 18650_holder |
| Plate, 35x25x3 mm, Steel | 4 | module_plate |
| Main PCB holding the Raspberry Pi Zero and the user interface PCB | 1 | main_pcb |
| Main PCB adapter to combine and raise the two connector fro the module pcb within the main module | 1 | main_pcb_adapter |
| Main PCB front panel as the case cover | 1 | main_pcb_front |
| Main PCB user interface holding a few buttons and an LED | 1 | main_pcb_ui |
| Module PCB with the LEDs | 10 | module_pcb |
| M4x10 wing screw (DIN 316) | 4 | |
| M3x4 countersunk head screw (ISO 14581) to hold the battery holders | 24 | |
| M3 nut (ISO 4032) to hold the battery holders in the main case | 4 | |
| M3x8 flat head screw (ISO7380) to hold the main PCB in the case | 4 | |
| M3 nut (ISO 4032) to hold the main PCB in the case | 4 | |
| M3x20 flat head screw (ISO7380) to hold the front panel PCB to the case | 4 | |
| M3 nut (ISO 4032) to hold the front panel PCB to the case | 4 | |
| M3x12 flat head screw (ISO7380) to hold the stand to the profile | 30 | |
| M3 nut (ISO 4032) to hold the stand to the profile | 30 | |
| M3x8 flat head screw (ISO7380) to hold the module PCB to the stand | 60 | |
| M3 nut (ISO 4032) to hold the module PCB to the stand | 60 | |
| M3x8 flat head screw (ISO7380) to hold the power button protector to the front panel PCB | 2 | |
| M3 nut (ISO 4032) to hold the power button protector to the front panel PCB | 2 | |
| M3x8 flat head screw (ISO7380) to hold the steel bolts to the profile | 16 | |
