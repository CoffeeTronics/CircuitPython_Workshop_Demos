# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import board
import displayio
from adafruit_apds9960.apds9960 import APDS9960

# FourWire is used for SPI bus
from fourwire import FourWire
# ST7789 is the display driver used for our TFT display
from adafruit_st7789 import ST7789

# Release any resources currently in use for the displays
displayio.release_displays()

# Instantiate SPI object for SPI bus using SPI peripheral
spi = board.SPI()
# Define pins used for SPI bus
tft_cs = board.D4
tft_dc = board.D6

# set up SPI display
display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = ST7789(display_bus, rotation=270, width=240, height=135,
                 rowstart=40, colstart=53)

i2c = board.I2C()  # uses board.SCL and board.SDA
apds = APDS9960(i2c)    # create instance of apds object for prox, gesture, color

# to read gestures, we need to enable both proximity & gesture
apds.enable_proximity = True
apds.enable_gesture = True

print("APDS9960 Gesture Detection!")

while True:
    
    gesture = apds.gesture()     # read gesture
    while gesture == 0:          # if no gesture, wait for a gesture
        gesture = apds.gesture() 
        
    # convert gesture reading into human readable format
    if gesture == 0x01:
        print("up")
    elif gesture == 0x02:
        print("down")
    elif gesture == 0x03:
        print("left")
    elif gesture == 0x04:
        print("right")
        

