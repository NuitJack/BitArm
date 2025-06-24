"""
TSC2046 Resistive Touch Controller Driver

Features:
- SPI interface communication
- Coordinate system with (0,0) at bottom-left
- Touch pressure detection
- Hardware IRQ support
- Configurable calibration

Coordinate System:
- X: 0.0 (left) to 1.0 (right)
- Y: 0.0 (bottom) to 1.0 (top)
- Z: Touch pressure (higher values = more pressure)
"""

import machine
import ustruct
import time

class TSC2046:
    """
    Driver for TSC2046 resistive touch controller.
    
    Command Definitions:
    CMD_X: Command to read X-axis (0x90)
    CMD_Y: Command to read Y-axis (0xD0)
    CMD_Z: Command to read pressure (0xB0)
    """
    
    # Command definitions
    CMD_X = 0x90
    CMD_Y = 0xD0
    CMD_Z = 0xB0

    def __init__(self, spi, cs, irq=None):
        """
        Initialize touch controller.
        
        Args:
            spi: Initialized SPI bus
            cs: Chip Select pin
            irq: Optional Interrupt pin
        """
        self.spi = spi
        self.cs = cs
        self.irq = irq
        self._calib = (0, 4095, 0, 4095)  # Default calibration (x_min, x_max, y_min, y_max)

        # Initialize pins
        self.cs.init(machine.Pin.OUT, value=1)
        if self.irq:
            self.irq.init(machine.Pin.IN, machine.Pin.PULL_UP)

    def _enable_cs(self):
        """Activate chip select with proper timing"""
        time.sleep_us(3)
        self.cs(0)
        time.sleep_us(3)

    def _disable_cs(self):
        """Deactivate chip select with proper timing"""
        time.sleep_us(3)
        self.cs(1)
        time.sleep_us(3)

    def _read_axis(self, cmd):
        """
        Read raw value from specified axis.
        
        Args:
            cmd: Measurement command (CMD_X, CMD_Y, CMD_Z)
            
        Returns:
            12-bit raw ADC value (0-4095)
        """
        self._enable_cs()
        self.spi.write(bytearray([cmd]))
        time.sleep_us(1)
        buf = bytearray(2)
        self.spi.readinto(buf)
        self._disable_cs()
        return ((buf[0] << 4) | (buf[1] >> 4)) & 0xFFF

    def set_calibration(self, calib):
        """
        Set calibration parameters for coordinate normalization.
        
        Args:
            calib: Tuple (x_min, x_max, y_min, y_max)
                   Raw ADC values at edges of touch area
        """
        self._calib = calib

    def read(self):
        """
        Read normalized touch coordinates and pressure.
        
        Returns:
            (x_norm, y_norm, z): Normalized coordinates and pressure
            x_norm: 0.0 (left) to 1.0 (right)
            y_norm: 0.0 (bottom) to 1.0 (top)
            z: Raw pressure value (0-4095, higher = more pressure)
        """
        # Read raw ADC values
        x = self._read_axis(self.CMD_X)
        y = self._read_axis(self.CMD_Y)
        z = self._read_axis(self.CMD_Z)
        
        # Unpack calibration values
        x_min, x_max, y_min, y_max = self._calib
        
        # Normalize X: 0.0 (left) to 1.0 (right)
        x_norm = (x - x_min) / (x_max - x_min)
        
        # Normalize Y: 0.0 (bottom) to 1.0 (top)
        # Note: Inverted because physical Y axis increases downward
        y_norm = (y_max - y) / (y_max - y_min)
        
        # Clamp to valid range
        x_norm = max(0.0, min(1.0, x_norm))
        y_norm = max(0.0, min(1.0, y_norm))
        
        return x_norm, y_norm, z

    def is_touched(self):
        """
        Check if screen is being touched.
        
        Uses IRQ pin if available, otherwise checks pressure.
        
        Returns:
            True if touched, False otherwise
        """
        return self.irq.value() == 0 if self.irq else (self.read()[2] > 100)