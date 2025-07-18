
"""CircuitPython CPU Temperature"""
import time
import microcontroller

def get_temp_F():
    return microcontroller.cpu.temperature * (9/5) + 32
    
def get_Temp_C():
    return microcontroller.cpu.temperature
    
while True:
    temp_C = get_Temp_C()
    temp_F = get_temp_F()
    print(f"Temp: {temp_C} C, {temp_F} F")
    time.sleep(0.5)