# Firmware compilation for RP Pico W integration with Touch LCD
If you just want to run this project without recompiling it's firmware, just download "firmware.uf2" and use it as instructed in the main README. The following text explains how it was compiled and how can you do it yourself.

## How to use this folder to compile RP's firmware
1. Clone this repository locally with `git clone https://github.com/NuitJack/BitArm.git`.
2. Download [this toolchain](https://developer.arm.com/-/media/Files/downloads/gnu/12.3.rel1/binrel/arm-gnu-toolchain-12.3.rel1-x86_64-arm-none-eabi.tar.xz?rev=dccb66bb394240a98b87f0f24e70e87d&hash=B788763BE143D9396B59AA91DBA056B6) from [ARM](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads), and unzip it inside the "`tools`" folder (see expected tree in the README file inside that folder).
3. Open a terminal inside this folder (`Firmware`).
4. Make sure that both "`build.sh`" and "`setup_submodules.sh`" have excecution permission (you can also run their command lines by hand, your choice).
5. Make sure that "CMake" and "make" are working properly on your computer.
6. Execute "`build.sh`". The first time will take longer, since it will update all of micropython's submodules before building.
7. The built firmware will be inside the generated "`build/output` folder.

This folder is building micropython v1.22.2 (editable within "`setup_submodules.sh`") with 4 modules from [BitDogLab](https://github.com/BitDogLab/BitDogLab/tree/main/libs)'s repository (`ahtx0.py`, `bh1750.py`, `matriz_bdl.py` and `ssd1306.py`) and 2 custom modules made to supply the needed comunication between the RP core and the Touch LCD display used (`ili9341.py` and `tsc2046.py`).

## How can I add my own python modules in the firmware?
1. Add the file with your module inside "`externals/libs`" (the file's name will be the name of the module)
2. Add the line `freeze("external/libs", "yourfilename.py")` at the end of "`manifest.py`"
3. Run "`build.sh`" and change the firmware file for the newly built one
4. Check if your module is avaliable with `help('modules')`
5. Add it to your "`main.py`" as usual (`include yourfilename`)
