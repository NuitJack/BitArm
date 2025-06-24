#!/bin/bash
set -e

# Configura submódulos (Feito manualmente)
./setup_submodules.sh > ./setup_output.log

# Limpa build anterior
cd external/micropython/ports/rp2
make clean
cd ../../../..
rm -rf build
mkdir -p build
cd build

# Executa CMake e Make
cmake .. -DCMAKE_TOOLCHAIN_FILE=../toolchain-arm-none-eabi.cmake > ./output.log
cmake --build . --target build_uf2 -j4 -- VERBOSE=1 >> output.log

echo "Build completo! UF2 em: build/output/firmware.uf2"