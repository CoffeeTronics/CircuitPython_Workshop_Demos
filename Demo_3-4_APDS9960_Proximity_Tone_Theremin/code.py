# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CircuitPython Analog Out example"""

# Change the value of analog_out.value to change frequency
import board
from analogio import AnalogOut
import adafruit_apds9960.apds9960
import displayio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from adafruit_st7789 import ST7789
from fourwire import FourWire
import time
import digitalio
import microcontroller
import neopixel

pixel_pin = board.NEOPIX
num_pixels = 5
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.1, auto_write=False)
# Turn off NeoPixels in case they were set on by a previous program
pixels.fill(0x000000)
pixels.show()

# Create instance of I2C object & BME680 object
i2c = board.I2C()
apds = adafruit_apds9960.apds9960.APDS9960(i2c)
# enable prox sensor in APDS9960
apds.enable_proximity = True

# This is the pin that will output the tone 
analog_out = AnalogOut(board.DAC)

# Release any resources currently in use for the display
displayio.release_displays()

# Instantiate SPI object for SPI bus using SPI peripheral
spi = board.LCD_SPI()
tft_cs = board.LCD_CS
tft_dc = board.D4

print("Create pin called 'backlight' for LCD backlight on PA06")
# backlight = digitalio.DigitalInOut(board.LCD_LEDA)
backlight = digitalio.DigitalInOut(microcontroller.pin.PA06)
backlight.direction = digitalio.Direction.OUTPUT
print("Turn TFT Backlight On")
backlight.value = True

# Init display bus for 1.14" display (240x135)
display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = ST7789(display_bus, rotation=90, width=240, height=135,
                 rowstart=40, colstart=53)

# Set text, font, and color and create four text labels
# Label text is placeholder text commonlu used in publishing for viewing layouts
font = bitmap_font.load_font("/Helvetica-Bold-16.bdf")
text_area1 = label.Label(font, text="APDS9960 Proximity ", color=0xFFFFFF)
text_area2 = label.Label(font, text="Theremin Demo", color=0xFFFFFF)


# Set positions for the labels
text_area1.x = 0
text_area1.y = 20

# The nested group's items can have their own coordinates relative to the nested group
text_area2.x = 0
text_area2.y = 50

# Create the parent group
parent_group = displayio.Group()

# Add the first label directly to the parent group
parent_group.append(text_area1)

# Create 3 nested groups for the other label
nested_group1 = displayio.Group()
nested_group1.append(text_area2)

# Append the nested groups to the parent group
parent_group.append(nested_group1)

# Show the parent group on the display
display.root_group = parent_group

# Show labels for 2 seconds
time.sleep(2)

def map_8bit_to_10bit_clamped(value_8bit):
    """Maps 8-bit value from prox to 10-bit for DAC"""
    return min(value_8bit << 2, 1023)

while True:
    prox = apds.proximity # returns 0-255
    dac_input = map_8bit_to_10bit_clamped(prox)
    # print("8-bit val:",prox, "10-bit val: ",dac_input,"\n")
    
    str1 = (f"Prox output: {prox} \n") 
    str2 = (f"DAC input: {dac_input} \n")
    
    text_area1.color = 0xFFFFFF
    text_area1.color = 0xFFFFFF
    
    text_area1.text = str1
    text_area2.text = str2
    
    if dac_input <= 5:
        analog_out.value = 0
    else:
        for i in range (0, 65535, dac_input):
            analog_out.value = i

