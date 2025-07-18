# When Cap Touch is detected on CAP1/A5 it writes to Serial Terminal
# and turns on LED (D13)

"""CircuitPython Essentials Capacitive Touch example"""
import time
import board
import touchio
import digitalio

touch_pad = board.A5  # CAP1/A5 is the capacitive touch pin
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

touch = touchio.TouchIn(touch_pad)

current_state = False
last_state = False

while True:
    last_state = current_state
    current_state = touch.value
    
    if (last_state and not current_state):
        print("Released!")
        led.value = False
    elif (current_state and not last_state):
        print("Touched!")
        led.value = True
        
    time.sleep(0.05)