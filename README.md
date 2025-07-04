# BitArm
This project uses a RP Pico W shielded by the [BitDogLab](https://bitdoglab.webcontent.website/) team's PCB to recieve user inputs through a 2.4-inch SPI TFT display with 240x320 resolution, ILI9341 controller, and resistive touchscreen (XPT2046) to control the movements of a 3D printed Robotic Arm via BLE comunication with an ESP32-DevKitC-32, controlling three MG90S metal gear servos for the arm's degrees of freedom and one SG90 servo motor for the claw. This was developed during the first semester of 2025 as a collaborative project for Unicamp's practical course on embedded systems projects at [FEEC](https://www.fee.unicamp.br/). In this repository you will find everything we used to bring this project into reality. We thank both the support and instruction of the course's professor, [Dr. Fabiano Fruett](http://lattes.cnpq.br/4840178785453194), whose vision made this and many other great projects' development possible with that practical course's offering.

<p align="center">
  <img src="https://github.com/NuitJack/BitArm/blob/main/Resources/BitArm_IMG/BitArmDemo.gif" alt="GIF with quick visual demo of the project" width="45%">
  <img src="https://github.com/NuitJack/BitArm/blob/main/Resources/BitArm_IMG/BitArmOverview.jpeg" alt="Picture of the project" width="45%">
</p>

> Follow [this Google Drive link](https://drive.google.com/file/d/1D46ARnqftNCbvr9nV22uoLGM8FUA34ID/view?usp=sharing) to see this demo in better resolution and detail

## Directory tree
```bash
BitArm/
├── Arm/	# Contains everything that was uploaded to our ESP32 in order to control the robotic arm via BLE sent commands coded unto individual chars
├── Firmware/	# Contains the firmware file and instructions on how to build a Firmware file for RP Pico W, already with custom drivers for the display's touch and LCD interfaces
├── Resources/	# All ilustrations used for this documentation
├── main.py	# The main python routine implemented into RP Pico W, responsible for running the main user interface
└── README.md	# This file
```

## Full material list
Main set of components:
- 1x BitDogLab kit, containing a Raspberry Pi Pico W microcontroler
- 1x 2.4-inch SPI TFT display with 240x320 resolution, ILI9341 controller, and resistive touchscreen (XPT2046) with plastic pen
- 1x ESP32-DevKitC-32 with CH340C USB-Serial converter
- 1x 38-pin ESP32S NodeMCU expander. With support for USB-C and Micro USB
- 1x 20000mAh/22.5W power bank with 5V output
- 1x USB to USB-C cable
- 3x MG90S motors (base and both joints)
- 3x MG90S Horn
- 1x SG90 motor (claw)
- 1x SG90 Horn

Arm Structure:
- Structure made of PLA filament with 3D printing
- 1x 608Zz bearing

Screws and Nuts:
- MG90S Motor Mounting
  - 6x M2 X 20mm Flat Head Screws 
  - 6x Nuts for M2 Screws
- 8 sets of (1 for Claw, 6 for Joint Supports, 1 for Axis):
  - 8x M2.5 X 20mm Pan Head Screws
  - 8x Nuts for M2.4 Screws
- Base
  - 4x M4 x 10mm Screws with Superb Thread

Display wiring acessories:
- 1x Breadboard 8.5×5.5cm (400 Holes)
- 8x Male-female jumpers
- 4x Male-male jumpers
- 1x 10kΩ resistor (for pull-up)

## I have everything ready, how can I run this project?
> Please note our code is built for running with BitDogLab's shield. Consider altering the needed code in main.py if you want to run this project on your own shield. From here onwards, we'll consider the usage of BitDogLab's shield and our main.py without any changes. 

1. (Optional) Build the custom firmware with the instructions provided in the "Firmware" directory's README
2. Upload the Firmware file (provided or built locally) to the RP Pico W. You can follow [BitDogLab's tutorial](https://github.com/BitDogLab/BitDogLab/tree/main/Firmware) for this step. We strongly recomend the usage of [Thonny IDE](https://thonny.org/), given it's ease of use. [This tutorial](https://bitdoglab.webcontent.website/cursos/introducao-pratica-a-bitdoglab/aulas/usando-o-ide-thonny-para-desenvolvimento/) (in portuguese) teaches how to setup the IDE and also upload the firmware file.
3. Connect the Touch LCD display to the avaliable RP pins according to the table bellow. We also provide an image on how it looks like when using a protoboard.

<div align="center">
  
| Function       | RP Pin  | Description           |
|----------------|---------|-----------------------|
| T_IRQ          | GND     | Touch Interrupt       |
| T_DO           | GP16    | Touch Data Output     |
| T_DIN          | GP19    | Touch Data Input      |
| T_CS           | GP9     | Touch Chip Select     |
| T_CLK          | GP18    | Touch Clock           |
| SDO (MISO)     | NC      | Not Connected         |
| LED            | 3V3     | Backlight Power       |
| SCK            | GP18    | SPI Clock             |
| SDI (MOSI)     | GP19    | SPI Data Input        |
| DC             | GP20    | Data/Command Control  |
| RESET          | 3V3 + 10kΩ | Reset with Pull-up |
| CS             | GP17    | Display Chip Select   |
| GND            | GND     | Ground                |
| VCC            | 3V3     | Power Supply          |

</div>

4. Upload the code present in the "Arm" directory, following its README, and connect the powerbank to start anouncing the BLE.
5. Turn on both ESP and RP sides and press the "A" button for starting the BLE connection process.
6. Wait until the initialization ends. The BitDogLab's OLED display and RBG LED are visual feedbacks of the commands given, providing information on the BLE communication and the delay needed to send the next command (LED color changes)
7. Each of the buttons changes the position 'state' of the arm, coding 8 different positions, and the opening and closing of the claw.
8. Long pressing the "Fechar" button ends the execution, shutting everything down. For running again, reset the RP, remove power from the ESP and go back to step 5.

## Final considerations
Feel free to use our project as a starting point for yours! We took heavy inspiration from [iwatake](https://github.com/iwatake2222)'s [pico-mnist](https://github.com/iwatake2222/pico-mnist) project for building the drivers for the Touch LCD display and also from [Thingiverse – Robotic Arm (MG90S based)](https://www.thingiverse.com/thing:1684471) for the arm and claw designs. So don't forget to credit us if this project was useful for you in any way!
