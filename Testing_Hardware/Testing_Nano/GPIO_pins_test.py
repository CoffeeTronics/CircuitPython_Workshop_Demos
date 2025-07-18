import board
from adafruit_boardtest import boardtest_gpio

# List out all the pins available to us
pins = [p for p in dir(board)]
print()
print("All pins found:", end=' ')

# Print pins
for p in pins:
    print(p, end=' ')
print('\n')

# Run test
result = boardtest_gpio.run_test(pins)
print()
print(result[0])
print("Pins tested: " + str(result[1]))