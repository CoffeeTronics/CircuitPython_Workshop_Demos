"""
This demo will initialize the display using displayio and draw a solid black
background, then read the BME680 data and write it to the TFT display in colors 
according to the thresholds defined (lines 44-59). It also shows on NeoPixels which range
each measurement is in.
NeoPixel Top Left: Temperature
NeoPixel Top Right: Humidity
NeoPixel Bottom Left: Barometric Pressure
NeoPixel Bottom Right: Gas
"""

import board
import adafruit_bme680
import time
import displayio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from adafruit_st7789 import ST7789
from fourwire import FourWire
import time
import digitalio
import microcontroller
from micropython import const
import math
import neopixel

RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

pixel_pin = board.NEOPIX
num_pixels = 5

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.1, auto_write=False)

# Turn off NeoPixels in case they were set on by a previous program
pixels.fill(0x000000)
pixels.show()

# Microchip Chandler office elevation = 362m above sea level - adjust for your location
CONST_ELEVATION = const(362)

CONST_TEMP_LOW = const(20)
CONST_TEMP_MED = const(25)
CONST_TEMP_HI = const(30)

CONST_HUMID_LOW = const(20)
CONST_HUMID_MED = const(40)
CONST_HUMID_HI = const(60)

CONST_PRESS_LOW = const(1000.0)  # Low pressure
CONST_PRESS_MED = const(1013.25)  # Standard pressure
CONST_PRESS_HI = const(1020.0)  # High pressure

# High resistance (Ohms) indicates better air quality
CONST_GAS_LOW = const(50000)
CONST_GAS_MED = const(48500)
CONST_GAS_HI = const(47000)

# Create instance of I2C object & BME680 object
i2c = board.I2C()
sensor = adafruit_bme680.Adafruit_BME680_I2C(i2c)

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

# Set text, font, and color and create four text labels
# Label text is placeholder text commonlu used in publishing for viewing layouts
font = bitmap_font.load_font("/Helvetica-Bold-16.bdf")
text_area1 = label.Label(font, text="Lorem ipsum dolor sit amet", color=0xFF00FF)
text_area2 = label.Label(font, text="consectetur adipiscing elit", color=0x0000FF)
text_area3 = label.Label(font, text="sed do eiusmod tempor incididunt ut", color=0xFF0000)
text_area4 = label.Label(font, text="labore et dolore magna aliqua", color=0x00FF00)

# Set positions for the labels
text_area1.x = 0
text_area1.y = 20

# The nested group's items can have their own coordinates relative to the nested group
text_area2.x = 0
text_area2.y = 50

text_area3.x = 0
text_area3.y = 80

text_area4.x = 0
text_area4.y = 110

# Create the parent group
parent_group = displayio.Group()

# Add the first label directly to the parent group
parent_group.append(text_area1)

# Create 3 nested groups for the other 3 labels
nested_group1 = displayio.Group()
nested_group1.append(text_area2)

nested_group2 = displayio.Group()
nested_group2.append(text_area3)

nested_group3 = displayio.Group()
nested_group3.append(text_area4)


# Optionally, you can offset the nested group within the parent group
# nested_group1.x = 20
# nested_group1.y = 0

# nested_group2.x = 20
# nested_group2.y = 0

# nested_group3.x = 20
# nested_group3.y = 0

# Append the nested groups to the parent group
parent_group.append(nested_group1)
parent_group.append(nested_group2)
parent_group.append(nested_group3)

# Show the parent group on the display
display.root_group = parent_group

# Show labels for 2 seconds
time.sleep(2)

# Main loop
while True:
    # Adjust sensor pressure reading for our elevation according
    # to the international Standard Atmosphere
    # Note: Atmospheric pressure changes with elevation.
    # The following code finds the equivalent pressure at sea level
    # to give accurate readings
    # in accordance with the international Standard Atmosphere.
    # The equation is: P0 = P1 (1 - (0.0065h/ (T + 0.0065h + 273.15))^(-5.257)
    # where:   P0 = calculated mean sea level pressure (hPa)
    # P1 = actual measured pressure (hPa))
    # h = elevation (m)
    # T = temp is degrees C
    temp = sensor.temperature
    mantissa = 1.0 - (0.0065 * CONST_ELEVATION /
                      (temp + (0.0065 * CONST_ELEVATION) + 273.15))
    adjustment = math.pow(mantissa, -5.257)
    pressure_adjusted = adjustment * sensor.pressure

    str1 = (f"Temperature: {sensor.temperature:.1f} C\n")
    str2 = (f"Humidity: {sensor.humidity:.1f} %\n")
    str3 = (f"Pressure: {pressure_adjusted:.1f} mB\n")
    str4 = (f"Gas: {sensor.gas} Ohms")	
	
    # set temperature text color according to thresholds
    if sensor.temperature <= CONST_TEMP_LOW:
        text_area1.color = 0x0000FF
        # Pixel 3 is top left
        pixels[3] = BLUE
        pixels.show()  
    elif (sensor.temperature > CONST_TEMP_MED and sensor.temperature <= CONST_TEMP_HI):
        text_area1.color = 0x00FF00
        # Pixel 3 is top left
        pixels[3] = GREEN
        pixels.show()  
        
    else:
        text_area1.color = 0xFF0000
        # Pixel 3 is top left
        pixels[3] = RED        
        pixels.show()        

    # set humidity text color according to thresholds
    if sensor.humidity <= CONST_HUMID_LOW:
        text_area2.color = 0x0000FF
        pixels[2] = BLUE
        pixels.show()  
    elif (sensor.humidity > CONST_HUMID_LOW and sensor.humidity <= CONST_HUMID_MED):
        text_area2.color = 0x00FF00
        pixels[2] = GREEN
        pixels.show() 
    else:
        text_area2.color = 0xFF0000
        pixels[2] = RED        
        pixels.show()

    # set pressure text color according to thresholds
    if pressure_adjusted <= CONST_PRESS_LOW:
        text_area3.color = 0x0000FF
        pixels[4] = BLUE
        pixels.show()
    elif (pressure_adjusted > CONST_PRESS_LOW and pressure_adjusted <= CONST_PRESS_MED):
        text_area3.color = 0x00FF00
        pixels[4] = GREEN
        pixels.show()
    else:
        text_area3.color = 0xFF0000
        pixels[4] = RED        
        pixels.show()

    # set gas text color according to thresholds
    if sensor.gas <= CONST_GAS_LOW:
        text_area4.color = 0x0000FF
        pixels[1] = BLUE
        pixels.show()
    elif (sensor.gas > CONST_GAS_LOW and sensor.gas <= CONST_GAS_MED):
        text_area4.color = 0x00FF00
        pixels[1] = GREEN
        pixels.show()
    else:
        text_area4.color = 0xFF0000
        pixels[1] = RED        
        pixels.show()

    text_area1.text = str1
    text_area2.text = str2
    text_area3.text = str3
    text_area4.text = str4

    time.sleep(1)
