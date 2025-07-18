import adafruit_sdcard
import busio
import digitalio
import board
import storage

# Connect to the card and mount the filesystem.
spi = busio.SPI(board.SD_SCK, board.SD_MOSI, board.SD_MISO)
cs = digitalio.DigitalInOut(board.SD_CS)
sdcard = adafruit_sdcard.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

# Use the filesystem as normal.
print("\nAbout to open new file test.txt")
with open("/sd/test.txt", "w") as f:
    f.write("Hello world\n")

with open("/sd/test.txt", "r") as f:
    print("Read line from file:")
    print(f.readline())

