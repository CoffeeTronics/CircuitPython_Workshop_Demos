# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import board
import displayio
# from adafruit_apds9960.apds9960 import APDS9960
from audiocore import WaveFile
import time
from audioio import AudioOut


# FourWire is used for SPI bus
# from fourwire import FourWire
# ST7789 is the display driver used for our TFT display
 

# Release any resources currently in use for the displays
displayio.release_displays()

# Instantiate SPI object for SPI bus using SPI peripheral
# spi = board.SPI()
# Define pins used for SPI bus
# tft_cs = board.D4
# tft_dc = board.D6

# set up SPI display
# display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs)
# display = ST7789(display_bus, rotation=270, width=240, height=135,
#                  rowstart=40, colstart=53)

# i2c = board.I2C()  # uses board.SCL and board.SDA
# apds = APDS9960(i2c)    # create instance of apds object for prox, gesture, color

# to read gestures, we need to enable both proximity & gesture
# apds.enable_proximity = True
# apds.enable_gesture = True

# Open WAV files to play for each gesture - note "rb" stands for "readable binary"
# WAV files need to be Mono 16-bit at 22kHz or less
wave_file_down = open("AudioFiles/140.wav", "rb")
wave_down = WaveFile(wave_file_down)

wave_file_up = open("AudioFiles/304.wav", "rb")
wave_up = WaveFile(wave_file_up)

wave_file_left = open("AudioFiles/210.wav", "rb")
wave_left = WaveFile(wave_file_left)

wave_file_right = open("AudioFiles/320.wav", "rb")
wave_right = WaveFile(wave_file_right)

# audio = AudioOut(board.A0)  # A0 is audio output pin
# audio = AudioOut(board.A1)
audio = AudioOut(board.DAC)

print("APDS9960 Gesture Detection!")

while True:

    print("up")
    audio.play(wave_up)
    time.sleep(2)
    print("down")
    audio.play(wave_down)
    time.sleep(2)
    print("left")
    audio.play(wave_left)
    time.sleep(2)
    print("right")
    audio.play(wave_right)
    time.sleep(2)


