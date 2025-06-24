import machine
import ustruct
import time

class ILI9341:
    """
    Driver for ILI9341 TFT LCD displays.
    
    Features:
    - Hardware SPI communication
    - Configurable display orientation
    - Text rendering with built-in font
    - Basic shapes (pixels, rectangles)
    - Display initialization and control
    
    Constants:
    FONT_WIDTH : Width of built-in font characters (5 pixels)
    FONT_HEIGHT: Height of built-in font characters (8 pixels)
    
    Memory Access Control Flags:
    MADCTL_MY : Row address order (bottom to top)
    MADCTL_MX : Column address order (right to left)
    MADCTL_MV : Row/column exchange (landscape mode)
    MADCTL_ML : Vertical refresh order
    MADCTL_BGR: BGR color filter (required for correct colors)
    MADCTL_MH : Horizontal refresh order
    
    Predefined Orientations:
    ORIENTATIONS: Dictionary mapping orientation names to MADCTL configurations:
        'PORTRAIT'       - Standard portrait (0°)
        'LANDSCAPE'      - Standard landscape (90°)
        'PORTRAIT_INV'   - Inverted portrait (180°)
        'LANDSCAPE_INV'   - Inverted landscape (270°)
    """

    # Constants
    FONT_WIDTH = 5
    FONT_HEIGHT = 8
    
    # Memory Access Control Flags
    MADCTL_MY   = 0x80  # Row Address Order
    MADCTL_MX   = 0x40  # Column Address Order
    MADCTL_MV   = 0x20  # Row/Column Exchange
    MADCTL_ML   = 0x10  # Vertical Refresh Order
    MADCTL_BGR  = 0x08  # BGR Color Filter
    MADCTL_MH   = 0x04  # Horizontal Refresh Order
    
    # Predefined Orientations
    ORIENTATIONS = {
        'PORTRAIT': MADCTL_MX | MADCTL_BGR,
        'LANDSCAPE': MADCTL_MV | MADCTL_BGR,
        'PORTRAIT_INV': MADCTL_MY | MADCTL_BGR,
        'LANDSCAPE_INV': MADCTL_MV | MADCTL_MY | MADCTL_BGR
    }

    def __init__(self, spi, dc, cs, WIDTH=320, HEIGHT=240, rst=None):
        """
        Initialize ILI9341 display controller.
        
        Default Configuration:
        - Orientation: LANDSCAPE_INV (270° rotation)
        - Text Direction: Left-to-Right (LTR)
        - Color Mode: 16-bit (RGB565)
        - Color Inversion: Enabled
        
        Args:
            spi: Initialized SPI bus
            dc: Data/Command control pin
            cs: Chip Select pin
            WIDTH: Display width in pixels (default 320)
            HEIGHT: Display height in pixels (default 240)
            rst: Optional Reset pin
        """
        self.spi = spi
        self.dc = dc
        self.cs = cs
        self.rst = rst
        
        # Runtime configuration with defaults
        self._width = WIDTH
        self._height = HEIGHT
        self._orientation = 'LANDSCAPE_INV'  # Default orientation
        self._text_direction = 'LTR'  # Default text direction
        self._char_spacing = 1
        self._line_spacing = 1
        self._fg_color = 0xFFFF  # White (RGB565)
        self._bg_color = 0x0000  # Black (RGB565)
        self._scale = 1
        self._inversion = False
        self._color_mode = 0x55  # 16-bit color (0x55 = RGB565)
        self._debug = False
        
        # Initialize hardware
        self._init_pins()
        self._init_display()

    def _init_pins(self):
        """Initialize control pins as outputs"""
        self.dc.init(machine.Pin.OUT)
        self.cs.init(machine.Pin.OUT)
        if self.rst:
            self.rst.init(machine.Pin.OUT)

    def _init_display(self):
        """Initialize display hardware sequence"""
        # Hardware reset if reset pin provided
        if self.rst:
            self.rst(0)
            time.sleep_ms(50)
            self.rst(1)
            time.sleep_ms(150)
        
        # Send initialization commands
        self._write_cmd(0x01)  # Software reset
        time.sleep_ms(150)
        self._write_cmd(0x11)  # Exit sleep mode
        time.sleep_ms(255)
        
        # Configure display orientation
        self._write_cmd(0x36)  # Memory Access Control (MADCTL)
        self._write_data(bytearray([self.ORIENTATIONS[self._orientation]]))
        
        # Set color mode
        self._write_cmd(0x3A)  # COLMOD - Interface Pixel Format
        self._write_data(bytearray([self._color_mode]))
        time.sleep_ms(10)
        
        # Enable color inversion
        self._write_cmd(0x21)  # Display Inversion ON
        time.sleep_ms(10)
        
        # Display on
        self._write_cmd(0x29)  # Display ON
        time.sleep_ms(100)
        
        # Clear screen to black
        self.fill(0)

    def _write_cmd(self, cmd):
        """Send command byte to display controller"""
        if self._debug: print(f"CMD: 0x{cmd:02X}")
        self.dc(0)  # Command mode
        self.cs(0)  # Select device
        self.spi.write(bytearray([cmd]))
        self.cs(1)  # Deselect device

    def _write_data(self, data):
        """Send data bytes to display controller"""
        if self._debug:
            if len(data) <= 8:
                print(f"DATA: {bytes(data).hex(' ')}")
            else:
                print(f"DATA: {len(data)} bytes")
        self.dc(1)  # Data mode
        self.cs(0)  # Select device
        self.spi.write(data)
        self.cs(1)  # Deselect device

    def set_window(self, x, y, w, h):
        """
        Set active drawing window boundaries.
        
        Defines a rectangular area for subsequent pixel writes.
        
        Args:
            x: Start X coordinate (0-based)
            y: Start Y coordinate (0-based)
            w: Window width in pixels
            h: Window height in pixels
        """
        # Column address set
        self._write_cmd(0x2A)  # CASET
        self._write_data(ustruct.pack(">HH", x, x + w - 1))
        
        # Row address set
        self._write_cmd(0x2B)  # RASET
        self._write_data(ustruct.pack(">HH", y, y + h - 1))
        
        # Prepare for memory write
        self._write_cmd(0x2C)  # RAMWR

    def fill(self, color):
        """Fill entire display with specified color"""
        self.fill_rect(0, 0, self._width, self._height, color)

    def pixel(self, x, y, color):
        """Draw a single pixel at specified coordinates"""
        self.set_window(x, y, 1, 1)
        self._write_data(ustruct.pack(">H", color))

    def fill_rect(self, x, y, w, h, color):
        """
        Draw a filled rectangle with specified color.
        
        Optimized for large areas by sending data in chunks.
        
        Args:
            x: Top-left X coordinate
            y: Top-left Y coordinate
            w: Rectangle width
            h: Rectangle height
            color: RGB565 color value
        """
        self.set_window(x, y, w, h)
        color_bytes = ustruct.pack(">H", color)
        pixel_count = w * h
        
        # Optimized block write parameters
        chunk_size = 512  # Bytes per transmission
        pixels_per_chunk = chunk_size // 2  # 2 bytes per pixel
        full_chunks = pixel_count // pixels_per_chunk
        remaining = pixel_count % pixels_per_chunk
        
        # Send full chunks
        chunk_data = color_bytes * pixels_per_chunk
        for _ in range(full_chunks):
            self._write_data(chunk_data)
        
        # Send remaining pixels
        if remaining:
            self._write_data(color_bytes * remaining)

    def draw_char(self, x, y, char, fg_color=None, bg_color=None, scale=None):
        """
        Render a single character using built-in font.
        
        Args:
            x: Top-left X coordinate
            y: Top-left Y coordinate
            char: Character to render
            fg_color: Foreground color (default: current setting)
            bg_color: Background color (default: current setting)
            scale: Scaling factor (default: 1)
            
        Returns:
            (width, height): Dimensions of rendered character
        """
        fg = fg_color if fg_color is not None else self._fg_color
        bg = bg_color if bg_color is not None else self._bg_color
        scale = scale if scale is not None else self._scale
        
        # Get ASCII code and validate range
        code = ord(char)
        if code < 32 or code > 126:
            code = 32  # Replace unsupported with space
        
        # Calculate font data position
        start_index = (code - 32) * 5
        font_data = self.DEFAULT_FONT[start_index:start_index+5]
        
        char_width = 5 * scale
        char_height = 8 * scale
        
        # Render character
        for col_idx in range(5):
            byte = font_data[col_idx]
            
            for row_idx in range(8):
                pixel_on = (byte >> (7 - row_idx)) & 0x01
                color = fg if pixel_on else bg
                
                # Draw scaled pixel
                if scale == 1:
                    self.pixel(x + col_idx, y + row_idx, color)
                else:
                    self.fill_rect(
                        x + col_idx * scale,
                        y + row_idx * scale,
                        scale,
                        scale,
                        color
                    )
        
        return char_width, char_height

    def text(self, text, x, y, fg_color=None, bg_color=None, scale=None, spacing=None):
        """
        Render text string using built-in font.
        
        Handles newline characters and configurable spacing.
        
        Args:
            text: String to render
            x: Start X coordinate
            y: Start Y coordinate
            fg_color: Text color (default: current setting)
            bg_color: Background color (default: current setting)
            scale: Character scaling factor (default: 1)
            spacing: Extra spacing between characters (default: 1px)
        """
        fg = fg_color if fg_color is not None else self._fg_color
        bg = bg_color if bg_color is not None else self._bg_color
        scale_val = scale if scale is not None else self._scale
        spacing_val = spacing if spacing is not None else self._char_spacing
        
        for char in text:
            if char == '\n':
                y += 8 * scale_val + self._line_spacing
                continue
            
            width, height = self.draw_char(x, y, char, fg, bg, scale_val)
            x += width + spacing_val

    # Built-in 5x8 pixel font (ASCII 32-126)
    DEFAULT_FONT = bytes([
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x5F, 0x00, 0x00, 0x00, 0x07, 0x00, 0x07, 0x00,
        0x14, 0x7F, 0x14, 0x7F, 0x14, 0x24, 0x2A, 0x7F, 0x2A, 0x12, 0x23, 0x13, 0x08, 0x64, 0x62,
        0x36, 0x49, 0x55, 0x22, 0x50, 0x00, 0x05, 0x03, 0x00, 0x00, 0x00, 0x1C, 0x22, 0x41, 0x00,
        0x00, 0x41, 0x22, 0x1C, 0x00, 0x08, 0x2A, 0x1C, 0x2A, 0x08, 0x08, 0x08, 0x3E, 0x08, 0x08,
        0x00, 0x50, 0x30, 0x00, 0x00, 0x08, 0x08, 0x08, 0x08, 0x08, 0x00, 0x60, 0x60, 0x00, 0x00,
        0x20, 0x10, 0x08, 0x04, 0x02, 0x3E, 0x51, 0x49, 0x45, 0x3E, 0x00, 0x42, 0x7F, 0x40, 0x00,
        0x42, 0x61, 0x51, 0x49, 0x46, 0x21, 0x41, 0x45, 0x4B, 0x31, 0x18, 0x14, 0x12, 0x7F, 0x10,
        0x27, 0x45, 0x45, 0x45, 0x39, 0x3C, 0x4A, 0x49, 0x49, 0x30, 0x01, 0x71, 0x09, 0x05, 0x03,
        0x36, 0x49, 0x49, 0x49, 0x36, 0x06, 0x49, 0x49, 0x29, 0x1E, 0x00, 0x36, 0x36, 0x00, 0x00,
        0x00, 0x56, 0x36, 0x00, 0x00, 0x00, 0x08, 0x14, 0x22, 0x41, 0x14, 0x14, 0x14, 0x14, 0x14,
        0x41, 0x22, 0x14, 0x08, 0x00, 0x02, 0x01, 0x51, 0x09, 0x06, 0x32, 0x49, 0x79, 0x41, 0x3E,
        0x7E, 0x11, 0x11, 0x11, 0x7E, 0x7F, 0x49, 0x49, 0x49, 0x36, 0x3E, 0x41, 0x41, 0x41, 0x22,
        0x7F, 0x41, 0x41, 0x22, 0x1C, 0x7F, 0x49, 0x49, 0x49, 0x41, 0x7F, 0x09, 0x09, 0x01, 0x01,
        0x3E, 0x41, 0x41, 0x51, 0x32, 0x7F, 0x08, 0x08, 0x08, 0x7F, 0x00, 0x41, 0x7F, 0x41, 0x00,
        0x20, 0x40, 0x41, 0x3F, 0x01, 0x7F, 0x08, 0x14, 0x22, 0x41, 0x7F, 0x40, 0x40, 0x40, 0x40,
        0x7F, 0x02, 0x04, 0x02, 0x7F, 0x7F, 0x04, 0x08, 0x10, 0x7F, 0x3E, 0x41, 0x41, 0x41, 0x3E,
        0x7F, 0x09, 0x09, 0x09, 0x06, 0x3E, 0x41, 0x51, 0x21, 0x5E, 0x7F, 0x09, 0x19, 0x29, 0x46,
        0x46, 0x49, 0x49, 0x49, 0x31, 0x01, 0x01, 0x7F, 0x01, 0x01, 0x3F, 0x40, 0x40, 0x40, 0x3F,
        0x1F, 0x20, 0x40, 0x20, 0x1F, 0x7F, 0x20, 0x18, 0x20, 0x7F, 0x63, 0x14, 0x08, 0x14, 0x63,
        0x07, 0x08, 0x70, 0x08, 0x07, 0x61, 0x51, 0x49, 0x45, 0x43, 0x00, 0x7F, 0x41, 0x41, 0x00,
        0x02, 0x04, 0x08, 0x10, 0x20, 0x00, 0x41, 0x41, 0x7F, 0x00, 0x04, 0x02, 0x01, 0x02, 0x04,
        0x40, 0x40, 0x40, 0x40, 0x40, 0x00, 0x01, 0x02, 0x04, 0x00, 0x20, 0x54, 0x54, 0x54, 0x78,
        0x7F, 0x48, 0x44, 0x44, 0x38, 0x38, 0x44, 0x44, 0x44, 0x20, 0x38, 0x44, 0x44, 0x48, 0x7F,
        0x38, 0x54, 0x54, 0x54, 0x18, 0x08, 0x7E, 0x09, 0x01, 0x02, 0x08, 0x14, 0x54, 0x54, 0x3C,
        0x7F, 0x08, 0x04, 0x04, 0x78, 0x00, 0x44, 0x7D, 0x40, 0x00, 0x20, 0x40, 0x44, 0x3D, 0x00,
        0x00, 0x7F, 0x10, 0x28, 0x44, 0x00, 0x41, 0x7F, 0x40, 0x00, 0x7C, 0x04, 0x18, 0x04, 0x78,
        0x7C, 0x08, 0x04, 0x04, 0x78, 0x38, 0x44, 0x44, 0x44, 0x38, 0x7C, 0x14, 0x14, 0x14, 0x08,
        0x08, 0x14, 0x14, 0x18, 0x7C, 0x7C, 0x08, 0x04, 0x04, 0x08, 0x48, 0x54, 0x54, 0x54, 0x20,
        0x04, 0x3F, 0x44, 0x40, 0x20, 0x3C, 0x40, 0x40, 0x20, 0x7C, 0x1C, 0x20, 0x40, 0x20, 0x1C,
        0x3C, 0x40, 0x30, 0x40, 0x3C, 0x44, 0x28, 0x10, 0x28, 0x44, 0x0C, 0x50, 0x50, 0x50, 0x3C,
        0x44, 0x64, 0x54, 0x4C, 0x44, 0x00, 0x08, 0x36, 0x41, 0x00, 0x00, 0x00, 0x7F, 0x00, 0x00,
        0x00, 0x41, 0x36, 0x08, 0x00, 0x08, 0x08, 0x2A, 0x1C, 0x08, 0x08, 0x1C, 0x2A, 0x08, 0x08
    ])