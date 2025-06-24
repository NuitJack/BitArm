# Firmware compilation for RP Pico W integration with Touch LCD
Step by step on how to use this folder to compile RP's firmware

1. Clone this repository locally with `git clone https://github.com/NuitJack/BitArm.git`
2. Download [this toolchain](https://developer.arm.com/-/media/Files/downloads/gnu/12.3.rel1/binrel/arm-gnu-toolchain-12.3.rel1-x86_64-arm-none-eabi.tar.xz?rev=dccb66bb394240a98b87f0f24e70e87d&hash=B788763BE143D9396B59AA91DBA056B6) from [ARM](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads), and unzip it inside the "tools" folder.
3. Open a terminal inside this folder
4. Check if both "build.sh" and "setup_submodules.sh" have excecution permission. If not, allow it (or be ready to run their commands by hand)
5. Make sure that "CMake" and "make" are working properly on your computer
6. Execute "build.sh". The first time will take longer, since it will update all of micropython's submodules before building
7. The built firmware will be inside the generated "build/output" folder

This folder is building micropython v1.22.2 (editable within "setup_submodules.sh") with 4 modules written from [BitDogLab](https://github.com/BitDogLab/BitDogLab/tree/main/libs)'s project (ahtx0.py, bh1750.py, matriz_bdl.py and ssd1306.py) and 2 custom modules made to supply the needed comunication between the RP core and the Touch LCD display used (ili9341.py and tsc2046.py).

You can also add your own python module with the following steps:
1. Add the file with your module inside "externals/libs" (the file's name will be the name of the module)
2. Add the line `freeze("external/libs", "yourfilename.py")` at the end of "manifest.py"
3. Run "build.sh" and change the firmware file for the newly built one
4. Check if your module is avaliable with `help('modules')`
5. Add it to your "main.py" as usual (`include yourfilename`)
