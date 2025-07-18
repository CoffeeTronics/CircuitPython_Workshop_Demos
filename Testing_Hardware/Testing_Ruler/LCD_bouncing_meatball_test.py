# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
This test will initialize the display using displayio and draw a solid black
background, a Microchip "Meatball" logo, and move the logo around the screen.
"""
import time
import board
# import terminalio
import displayio
import adafruit_imageload
import digitalio
import microcontroller

# Starting in CircuitPython 9.x fourwire will be a seperate internal library
# rather than a component of the displayio library
try:
    from fourwire import FourWire
except ImportError:
    from displayio import FourWire
# from adafruit_display_text import label
from adafruit_st7789 import ST7789

# NEED A NEW BUILD TO GIVE PIN PA06 A BOARD NAME!!
print("Create pin called 'backlight' for LCD backlight on PA06")
backlight = digitalio.DigitalInOut(microcontroller.pin.PA06)
backlight.direction = digitalio.Direction.OUTPUT

print("Release displays")
# Release any resources currently in use for the displays
displayio.release_displays()

print("Create SPI Object for display")
tft_spi = board.LCD_SPI()
tft_cs = board.LCD_CS
tft_dc = board.D4

WIDTH = 240
HEIGHT = 135
LOGO_WIDTH = 32
LOGO_HEIGHT = 30

print("Create DisplayBus")
display_bus = FourWire(tft_spi, command=tft_dc, chip_select=tft_cs)
display = ST7789(
    display_bus, rotation=90, width=WIDTH, height=HEIGHT, rowstart=40, colstart=53
)
print("Load Sprite sheet")
# Load the sprite sheet (bitmap)
sprite_sheet, palette = adafruit_imageload.load("/Meatball_32x30_16color.bmp",
                                                bitmap=displayio.Bitmap,
                                                palette=displayio.Palette)
print("Create Sprite")
# Create a sprite (tilegrid)
sprite = displayio.TileGrid(sprite_sheet, pixel_shader=palette,
                            width=1,
                            height=1,
                            tile_width=LOGO_WIDTH,
                            tile_height=LOGO_HEIGHT)
                            
print("Create Group to hold Sprite")
# Create a Group to hold the sprite
group = displayio.Group(scale=1)

print("Append Sprite to Group")
# Add the sprite to the Group
group.append(sprite)

print("Add Group to Display")
# Add the Group to the Display
display.root_group = group

print("Set Sprite Initial Location")
# Set sprite location
group.x = 150
group.y = 70

ReachedRightSide = False
ReachedLeftSide = True
ReachedBottomSide = False
ReachedTopSide = True

print("About to start while(1) loop")
print("About to start while(1) loop")


print("Turn D5 LEDA On")
backlight.value = True

while True:

    if ReachedLeftSide is True:
        group.x += 2
    if ReachedRightSide is True:
        group.x -= 2
    if ReachedTopSide is True:
        group.y += 3
    if ReachedBottomSide is True:
        group.y -= 3

    if group.x >= WIDTH - LOGO_WIDTH:
        ReachedRightSide = True
        ReachedLeftSide = False
    if group.x <= 0:
        ReachedRightSide = False
        ReachedLeftSide = True
    if group.y >= HEIGHT - LOGO_HEIGHT:
        ReachedBottomSide = True
        ReachedTopSide = False
    if group.y <= 0:
        ReachedBottomSide = False
        ReachedTopSide = True

    time.sleep(0.05)


