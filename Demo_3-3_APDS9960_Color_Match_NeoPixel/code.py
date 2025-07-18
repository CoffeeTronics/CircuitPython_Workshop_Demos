import board
import displayio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from adafruit_st7789 import ST7789
from fourwire import FourWire
import time
import adafruit_apds9960.apds9960
import digitalio
import microcontroller
import neopixel

pixel_pin = board.NEOPIX
num_pixels = 5

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.7, auto_write=False)

# Turn off NeoPixels in case they were set on by a previous program
pixels.fill(0x000000)
pixels.show()

# This is used to map the 16-bit RGB values from
# APDS9960 to 8 bit values used by NeoPixels
NUM_BITSHIFTS_NEOPIXEL = 8

# Create instance of I2C object & BME680 object
i2c = board.I2C()
sensor = adafruit_apds9960.apds9960.APDS9960(i2c)
# enable color sensor in APDS9960
sensor.enable_color = True

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
text_area1 = label.Label(font, text="Red Content", color=0xFF0000)
text_area2 = label.Label(font, text="Green Content", color=0x00FF00)
text_area3 = label.Label(font, text="Blue Content", color=0x0000FF)
text_area4 = label.Label(font, text="Clear Content", color=0xFFFFFF)

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
    r,g,b,c = sensor.color_data
    print("Red: ",r, "Green: ",g, "Blue: ",b, "Clear: ",c)

    str1 = (f"RED: {r} \n")
    str2 = (f"GREEN: {g} \n")
    str3 = (f"BLUE: {b} \n")
    str4 = (f"CLEAR: {c} ")

    
    text_area1.color = 0xFF0000
    text_area2.color = 0x00FF00
    text_area3.color = 0x0000FF
    text_area4.color = 0xFFFFFF

    text_area1.text = str1
    text_area2.text = str2
    text_area3.text = str3
    text_area4.text = str4
    
    r_shifted = r >> 8
    g_shifted = g >> 8
    b_shifted = b >> 8
    
    print("Red: ",r_shifted, "Green: ",g_shifted, "Blue: ", b_shifted, "Clear: ", c)
    
    neopixel_color = (r_shifted << 16) | (g_shifted << 8) | (b_shifted)  
    # neopixel_color = (r << 16) | (g << 8) | (b)
      
    # Match color sensors values on NeoPixels
    pixels.fill(neopixel_color)
    # turn off Nano pixel
    pixels[0] = 0x000000
    pixels.show()

    time.sleep(0.5)
