include("$(PORT_DIR)/boards/manifest.py")

# Congela os módulos personalizados
freeze("external/libs", "ahtx0.py")
freeze("external/libs", "bh1750.py")
freeze("external/libs", "ssd1306.py", opt=3)
freeze("external/libs", "matriz_bdl.py")
freeze("external/libs", "ili9341.py")
freeze("external/libs", "tsc2046.py")