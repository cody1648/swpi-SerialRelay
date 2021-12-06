# coding: UTF-8
import threading
import serial
import time

threadlock = threading.Lock()

p1 = serial.Serial(
                port='/dev/ttyUSB0',
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=None
            )

p2 = serial.Serial(
                port='/dev/ttyUSB1',
                baudrate=115200,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=None
            )

def readp1():
    while True:
        str = p1.readline().decode()
        print(f'1:{str}')
def readp2():
    while True:
        str = p2.readline().decode()
        print(f'2:{str}')

def writep2():
    i = 0
    while True:
        i = i + 1
        _str = str(i)
        with threadlock:
            p2.write(_str.encode() + b'\r\n')
            p2.readline()
            if b'*ok\r\n' != p2.readline():
                print('cannot receive data correctly')
        time.sleep(1)

t1 = threading.Thread(target=readp1)
t2 = threading.Thread(target=readp2)
t3 = threading.Thread(target=writep2)
t1.start()
t2.start()
t3.start()