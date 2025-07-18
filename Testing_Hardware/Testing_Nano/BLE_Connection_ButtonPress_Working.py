import board
import busio
import time
import digitalio

ble = busio.UART(board.BLE_TX, board.BLE_RX, baudrate=115200)

# create BLE_CLR digitalio pin
ble_reset = digitalio.DigitalInOut(board.BLE_CLR)
ble_reset.direction = digitalio.Direction.OUTPUT

# set up User Button
usr_btn = digitalio.DigitalInOut(board.D3)
usr_btn.direction = digitalio.Direction.INPUT

# set BLE_CLR pin LOW for 200ms
ble_reset.value = False
print("Reset LOW for 200ms")
time.sleep(0.2)
print("Reset HIGH")
ble_reset.value = True
time.sleep(1.0)

command = "$"
# command = "-"

for i in range(3):
    data_Tx = ble.write(bytes(f"{command}", "ascii"))
    time.sleep(0.2)
data_Tx = ble.write("\r\n")
print("Command mode sent")

time.sleep(0.5)
data_Rx = ble.read(20)
print("Data received:", data_Rx)

# command1 = "(SR,"
# command2 = 0001
time.sleep(0.5)
print("Enable BLE status indication")
# data_Tx = ble.write(bytes(f"{command1}", "ascii"))
# data_Tx = ble.write(bytes(f"{command2}", "hex"))
# data_Tx = ble.write(")\r\n")
data_Tx = ble.write("SR,0001\r\n")
time.sleep(0.5)
data_Rx = ble.read(20)
print("Data received:", data_Rx)

time.sleep(0.5)
print("Sending Reboot Command")
data_Tx = ble.write("R,1")
data_Tx = ble.write("\r\n")
time.sleep(0.5)
data_Rx = ble.read(20)
print("Data received:", data_Rx)

last_btn_state = False

while True:
    # read button state
    btn_val = usr_btn.value

    if (not btn_val and last_btn_state):
        print("User Button Pressed!\r\n")
        data_Tx = ble.write("Button Pressed!\r\n")
    elif (btn_val and (not last_btn_state)):
        print("User Button Released!\r\n")
        data_Tx = ble.write("Button Released!\r\n")

    # save button state for next time
    last_btn_state = btn_val