# BitArm
This project uses a RP Pico W shielded by the [BitDogLab](https://bitdoglab.webcontent.website/) team's PCB to recieve user inputs through a (Touch LCD display) to control the movements of a 3D printed Robotic Arm via BLE comunication with an ESP32-DevKitC-32, controlling three MG90S metal gear servos for the arm's degrees of freedom and one SG90 servo motor for the tong. This was developed during the first semester of 2025 as a collaborative project for Unicamp's practical course on embedded systems projects at [FEEC](https://www.fee.unicamp.br/). In this repository you will find everything we used to bring this project into reality. We thank both the support and instruction of the course's professor, [Dr. Fabiano Fruett](http://lattes.cnpq.br/4840178785453194), whose vision made this and many other great projects' development possible.

(Insert image and description)

(Insert gif and description)

## Directory tree
```bash
BitArm/
├── Arm/	# Contains everything that was uploaded to our ESP32 in order to control the robotic arm via BLE sent commands coded unto individual chars
├── Firmware/	# Contains instructions on how to build a Firmware file onto RP Pico W already with custom drivers for the display's touch and LCD interfaces
├── Resources/	# All ilustrations used for this documentation
├── main.py	# The main python routine implemented into RP Pico W, responsible for running the main user interface
└── README.md	# This file
```

## Full material list

## I have everything ready, how can I run this project?
> Please note our code is built for running with BitDogLab's shield. Consider altering the needed code in main.py if you want to run this project on your own shield. From here onwards, we'll consider the usage of BitDogLab's shield and our main.py without any changes. 

1. (Optional) Build the custom firmware with the instructions provided in the "Firmware" directory's README
2. Upload the Firmware file (provided or built locally) to the RP Pico W. You can follow [BitDogLab's tutorial](https://github.com/BitDogLab/BitDogLab/tree/main/Firmware) for this step. We strongly recomend the usage of [Thonny IDE](https://thonny.org/), given it's ease of use. [This tutorial](https://bitdoglab.webcontent.website/cursos/introducao-pratica-a-bitdoglab/aulas/usando-o-ide-thonny-para-desenvolvimento/) (in portuguese) teaches how to setup the IDE and also upload the firmware file.
3. Connect the Touch LCD display to the avaliable RP pins according to the table bellow. We also provide an image on how it looks like when using a protoboard.

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

(Add image with connections)

4. (Instructions regarding ESP)
5. Turn on both ESP and RP sides and press the "A" button for starting the BLE connection process.
6. Wait until the initialization ends. The BitDogLab's OLED display and RBG LED are visual feedbacks of the commands given, providing information on the BLE communication and the delay needed to send the next command (LED color changes)
7. Each of the buttons changes the position 'state' of the arm, coding 8 different positions, and the opening and closing of the tong.
8. Long pressing the "Fechar" button ends the execution, shutting everything down. For running again, reset the RP, remove power from the ESP and go back to step 5.

## Final considerations
Feel free to use our project as a starting point for yours! We took heavy inspiration from [iwatake](https://github.com/iwatake2222)'s [pico-mnist](https://github.com/iwatake2222/pico-mnist) project for building the drivers for the Touch LCD display and also from (Insert project inspiration for arm). So don't forget to credit us if this project was useful for you in any way!
