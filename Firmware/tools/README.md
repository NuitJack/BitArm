This is where you should unpack the arm toolchain. Running `tree -L 3` here should result in:
```.
└── arm-gnu-toolchain-12.3.rel1-x86_64-arm-none-eabi
    ├── 12.3.rel1-x86_64-arm-none-eabi-manifest.txt
    ├── arm-none-eabi
    │   ├── bin
    │   ├── include
    │   └── lib
    ├── bin
    │   ├── arm-none-eabi-addr2line
    │   ├── arm-none-eabi-ar
    │   ├── arm-none-eabi-as
    │   ├── arm-none-eabi-c++
    │   ├── arm-none-eabi-c++filt
    │   ├── arm-none-eabi-cpp
    │   ├── arm-none-eabi-elfedit
    │   ├── arm-none-eabi-g++
    │   ├── arm-none-eabi-gcc
    │   ├── arm-none-eabi-gcc-12.3.1
    │   ├── arm-none-eabi-gcc-ar
    │   ├── arm-none-eabi-gcc-nm
    │   ├── arm-none-eabi-gcc-ranlib
    │   ├── arm-none-eabi-gcov
    │   ├── arm-none-eabi-gcov-dump
    │   ├── arm-none-eabi-gcov-tool
    │   ├── arm-none-eabi-gdb
    │   ├── arm-none-eabi-gdb-add-index
    │   ├── arm-none-eabi-gfortran
    │   ├── arm-none-eabi-gprof
    │   ├── arm-none-eabi-ld
    │   ├── arm-none-eabi-ld.bfd
    │   ├── arm-none-eabi-lto-dump
    │   ├── arm-none-eabi-nm
    │   ├── arm-none-eabi-objcopy
    │   ├── arm-none-eabi-objdump
    │   ├── arm-none-eabi-ranlib
    │   ├── arm-none-eabi-readelf
    │   ├── arm-none-eabi-size
    │   ├── arm-none-eabi-strings
    │   └── arm-none-eabi-strip
    ├── include
    │   └── gdb
    ├── lib
    │   ├── bfd-plugins
    │   └── gcc
    ├── libexec
    │   └── gcc
    ├── license.txt
    └── share
        ├── doc
        ├── gcc-12.3.1
        ├── gcc-arm-none-eabi
        ├── gdb
        ├── info
        └── man

21 directories, 33 files
```
