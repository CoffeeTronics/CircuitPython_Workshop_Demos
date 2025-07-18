# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
This demo will initialize the display using displayio and draw a solid black
background, a Microchip "Meatball" logo, and move the logo around the screen.
"""
import time
import board
import adafruit_icm20x
# import terminalio
import displayio
import adafruit_imageload

# Starting in CircuitPython 9.x fourwire will be a seperate internal library
# rather than a component of the displayio library
try:
    from fourwire import FourWire
except ImportError:
    from displayio import FourWire
# from adafruit_display_text import label
from adafruit_st7789 import ST7789from adafruit_st7789 import ST7789

i2c = board.I2C()  # uses board.SCL and board.SDA
icm = adafruit_icm20x.ICM20948(i2c)

# Release any resources currently in use for the displays
displayio.release_displays()

spi = board.SPI()
tft_cs = board.D4
tft_dc = board.D6

WIDTH = 240
HEIGHT = 135
LOGO_WIDTH = 32
LOGO_HEIGHT = 30

display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = ST7789(
    display_bus, rotation=270, width=WIDTH, height=HEIGHT, rowstart=40, colstart=53
)

# Load the sprite sheet (bitmap)
sprite_sheet, palette = adafruit_imageload.load("/Meatball_32x30_16color.bmp",
                                                bitmap=displayio.Bitmap,
                                                palette=displayio.Palette)

# Create a sprite (tilegrid)
sprite = displayio.TileGrid(sprite_sheet, pixel_shader=palette,
                            width=1,
                            height=1,
                            tile_width=LOGO_WIDTH,
                            tile_height=LOGO_HEIGHT)

# Create a Group to hold the sprite
group = displayio.Group(scale=1)

# Add the sprite to the Group
group.append(sprite)

# Add the Group to the Display
display.root_group = group

# Set sprite location
group.x = 150
group.y = 70

X_pos = 150
Y_pos = 70

while True:

    X, Y, Z = icm.acceleration

    print("X: {:.2f}".format(X))
    print("Y: {:.2f}".format(Y))
    print("Z: {:.2f}".format(Z))
    print("")

    X_pos -= int(X)
    Y_pos += int(Y)

    if X_pos >= WIDTH - LOGO_WIDTH:
        group.x = WIDTH - LOGO_WIDTH
        X_pos = WIDTH - LOGO_WIDTH
    else:
        group.x = X_pos

    if X_pos <= 0:
        group.x = 0
        X_pos = 0
    else:
        group.x = X_pos

    if Y_pos >= HEIGHT - LOGO_HEIGHT:
        group.y = HEIGHT - LOGO_HEIGHT
        Y_pos = HEIGHT - LOGO_HEIGHT
    else:
        group.y = Y_pos

    if Y_pos <= 0:
        group.y = 0
        Y_pos = 0
    else:
        group.y = Y_pos

    time.sleep(0.05)







