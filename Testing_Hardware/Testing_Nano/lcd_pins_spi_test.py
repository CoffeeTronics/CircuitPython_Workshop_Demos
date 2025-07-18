import time
import microcontroller
import digitalio
import busio

spi = busio.SPI(microcontroller.pin.PA05, MOSI=microcontroller.pin.PA04)
cs = digitalio.DigitalInOut(microcontroller.pin.PA07)
cs.direction = digitalio.Direction.OUTPUT
cs.value = True

while True:

    while not spi.try_lock():
        pass
       
    try:
        spi.configure(baudrate=5000000, phase=0, polarity=0)
        cs.value = False
        spi.write(bytes([0x02, 0xFE]))
        cs.value = True
    finally:
        spi.unlock()
    
    time.sleep(1)




