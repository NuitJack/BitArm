# Configurações básicas do sistema
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR arm)

# Caminho do toolchain
set(TOOLCHAIN_PATH "${CMAKE_SOURCE_DIR}/tools/arm-gnu-toolchain-12.3.rel1-x86_64-arm-none-eabi")

# Configuração dos compiladores
set(CMAKE_C_COMPILER "${TOOLCHAIN_PATH}/bin/arm-none-eabi-gcc")
set(CMAKE_CXX_COMPILER "${TOOLCHAIN_PATH}/bin/arm-none-eabi-g++")
set(CMAKE_ASM_COMPILER "${TOOLCHAIN_PATH}/bin/arm-none-eabi-gcc")
set(CMAKE_AR "${TOOLCHAIN_PATH}/bin/arm-none-eabi-ar")
set(CMAKE_OBJCOPY "${TOOLCHAIN_PATH}/bin/arm-none-eabi-objcopy")
set(CMAKE_SIZE "${TOOLCHAIN_PATH}/bin/arm-none-eabi-size")

# Configuração de busca de arquivos
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)

set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)  # Ignora testes de linker
set(CMAKE_C_FLAGS "-mcpu=cortex-m0plus -mthumb -nostdlib" CACHE STRING "")
set(CMAKE_CXX_FLAGS "${CMAKE_C_FLAGS}" CACHE STRING "")

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -D_POSIX_C_SOURCE=200809L -D_GNU_SOURCE -Wno-error=unused-variable")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -D_POSIX_C_SOURCE=200809L -D_GNU_SOURCE -Wno-error=unused-variable")