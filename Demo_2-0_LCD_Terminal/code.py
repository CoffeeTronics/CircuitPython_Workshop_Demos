# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
This test will initialize the display using displayio and use the display
as a terminal. This terminal will mirror the output in the Mu Serial Terminal.
"""
import time
import board
import displayio

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

display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = ST7789(display_bus, rotation=270, width=240, height=135,
                 rowstart=40, colstart=53)

# Initialize integer value to be printed in Serial Terminal
val = 0

while True:
    # Print to terminal
    print("Val: ", val)
    # Sleep for 1 second
    time.sleep(1)
    # Increment variable for next time through loop
    val += 1
