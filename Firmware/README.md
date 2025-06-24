# Firmware compilation for RP Pico W integration with Touch LCD
Step by step on how to use this folder to compile RP's firmware

1. Clone this repository locally with `git clone https://github.com/NuitJack/BitArm.git`
2. Download [this toolchain](https://developer.arm.com/-/media/Files/downloads/gnu/12.3.rel1/binrel/arm-gnu-toolchain-12.3.rel1-x86_64-arm-none-eabi.tar.xz?rev=dccb66bb394240a98b87f0f24e70e87d&hash=B788763BE143D9396B59AA91DBA056B6) from [ARM](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads), and unzip it inside the "tools" folder.
3. Open a terminal inside this folder
4. Check if both "build.sh" and "setup_submodules.sh" have excecution permission. If not, allow it (or be ready to run their commands by hand)
5. Make sure that "CMake" and "make" are working properly on your computer
6. Execute "build.sh". The first time will take longer, since it will update all of micropython's submodules before building
7. The built firmware will be inside the generated "build/output" folder
