cmake_minimum_required(VERSION 3.12)
project(MicroPython_RP2040 NONE)

set(TOOLCHAIN_DIR "${CMAKE_SOURCE_DIR}/tools/arm-gnu-toolchain-12.3.rel1-x86_64-arm-none-eabi")
set(CROSS_COMPILE "${TOOLCHAIN_DIR}/bin/arm-none-eabi-")

# Primeiro compile mpy-cross com o compilador do host
add_custom_target(
    build_mpycross
    COMMAND make -C ${CMAKE_SOURCE_DIR}/external/micropython/mpy-cross
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Compilando mpy-cross..."
)

# Depois compile o firmware
add_custom_target(
    build_uf2 ALL
    DEPENDS build_mpycross
    COMMAND mkdir -p ${CMAKE_BINARY_DIR}/output
    COMMAND make -C ${CMAKE_SOURCE_DIR}/external/micropython/ports/rp2
        BOARD=RPI_PICO_W
        CROSS_COMPILE=${CROSS_COMPILE}
        FROZEN_MANIFEST=${CMAKE_SOURCE_DIR}/manifest.py
        LDFLAGS_EXTRA="-Wl,--whole-archive -lstdc++ -Wl,--no-whole-archive"
    COMMAND cp 
        ${CMAKE_SOURCE_DIR}/external/micropython/ports/rp2/build-RPI_PICO_W/firmware.uf2
        ${CMAKE_BINARY_DIR}/output/
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Construindo firmware para RPI_PICO_W..."
)