# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
This demo will initialize the display using displayio and draw a solid black
background, a Microchip "Meatball" logo, and move the logo around the screen from the IMU data
"""
import time
import board
import adafruit_icm20x
# import terminalio
import displayio
import adafruit_imageload
import digitalio
import microcontroller
import neopixel

pixel_pin = board.NEOPIX
num_pixels = 5

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.1, auto_write=False)

# Turn off NeoPixels in case they were set on by a previous program
pixels.fill(0x000000)
pixels.show()

# Starting in CircuitPython 9.x fourwire will be a seperate internal library
# rather than a component of the displayio library
try:
    from fourwire import FourWire
except ImportError:
    from displayio import FourWire
# from adafruit_display_text import label
from adafruit_st7789 import ST7789

i2c = board.I2C()  # uses board.SCL and board.SDA
icm = adafruit_icm20x.ICM20948(i2c)

print("Create pin called 'backlight' for LCD backlight on PA06")
# backlight = digitalio.DigitalInOut(board.LCD_LEDA)
backlight = digitalio.DigitalInOut(microcontroller.pin.PA06)
backlight.direction = digitalio.Direction.OUTPUT

# Release any resources currently in use for the displays
print("Release displays")
displayio.release_displays()

print("Create SPI Object for display")
spi = board.LCD_SPI()
tft_cs = board.LCD_CS
tft_dc = board.D4

print("Turn TFT Backlight On")
backlight.value = True

WIDTH = 240
HEIGHT = 135
LOGO_WIDTH = 32
LOGO_HEIGHT = 30

print("Create DisplayBus")
display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = ST7789(
    display_bus, rotation=90, width=WIDTH, height=HEIGHT, rowstart=40, colstart=53
)

# Load the sprite sheet (bitmap)
print("Load Sprite sheet")
sprite_sheet, palette = adafruit_imageload.load("/Meatball_32x30_16color.bmp",
                                                bitmap=displayio.Bitmap,
                                                palette=displayio.Palette)

# Create a sprite (tilegrid)
print("Create Sprite")
sprite = displayio.TileGrid(sprite_sheet, pixel_shader=palette,
                            width=1,
                            height=1,
                            tile_width=LOGO_WIDTH,
                            tile_height=LOGO_HEIGHT)

# Create a Group to hold the sprite
print("Create Group to hold Sprite")
group = displayio.Group(scale=1)

# Add the sprite to the Group
print("Append Sprite to Group")
group.append(sprite)

# Add the Group to the Display
print("Add Group to Display")
display.root_group = group

# Set sprite location
print("Set Sprite Initial Location")
group.x = 150
group.y = 70

X_pos = 150
Y_pos = 70

while True:

    X, Y, Z = icm.acceleration

    # print("X: {:.2f}".format(X))
    # print("Y: {:.2f}".format(Y))
    # print("Z: {:.2f}".format(Z))
    # print("")

    X_pos += int(X)
    Y_pos -= int(Y)

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







