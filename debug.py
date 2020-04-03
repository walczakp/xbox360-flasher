from datetime import datetime

import serial

ser = serial.Serial('COM3', baudrate=9600)

ser.flushInput()
printdate = True


while True:
    try:
        char = (ser.read(1)).decode('ascii')
        if printdate:
            print(datetime.now(), end="\t")
            printdate = False

        if char == '\n':
            printdate = True
        print(char, end="")
    except serial.SerialException:
        ser = serial.Serial('COM3', baudrate=9600)
        continue

