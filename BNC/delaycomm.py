import serial

ser = serial.Serial('COM5',115200, timeout=1)

ser.write(":PULS2:DEL?")
delayB = ser.readline()
print(delayB)

ser.close()
