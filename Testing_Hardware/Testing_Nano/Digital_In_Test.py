
import board
import digitalio

# Enter Digital pin D0 - D7, D13, A0-A5
switch = digitalio.DigitalInOut(board.A0)
switch.direction = digitalio.Direction.INPUT

while True:
    if switch.value is False:
        print("Switch is on!")
    else:
        print("Switch is off!")
