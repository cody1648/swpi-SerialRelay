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
p1.reset_input_buffer()
p1.reset_output_buffer()
p2.reset_input_buffer()
p2.reset_output_buffer()

def readp1():
    while True:
        threadlock.acquire()
        str = p1.readline()
        print(f'1:{repr(str.decode())}')
        p2.write(str)
        p2.read_until(b'*ok\r\n')
        threadlock.release()

def readp2():
    while True:
        str = repr(p2.readline().decode())
        print(f'2:{str}')

def writep1():
    p1.write(b'\r')
    time.sleep(5)
    i = 0
    while True:
        # i = i + 1
        # _str = str(i)
        _str = 'show arp'
        threadlock.acquire()
        print("sendtoSW:" + _str)
        p1.write(_str.encode())
        p1.write(b'\r')
        # p1.readline()
        # if b'*ok\r\n' != p1.readline():
        #     print('cannot receive data correctly')
        threadlock.release()
        time.sleep(30)    

def writep2():
    time.sleep(5)
    i = 0
    while True:
        i = i + 1
        _str = str(i)
        # threadlock.acquire()
        print("sendtoLRA1:" + _str)
        p2.write(_str.encode() + b'\r\n')
        # p2.readline()
        # if b'*ok\r\n' != p2.readline():
        #     print('cannot receive data correctly')
        # threadlock.release()
        time.sleep(5)

def statPort():
    while True:
        time.sleep(10)
        if p1.isOpen():
            print('port0:Open')
        else:
            print('port0:Not open')

        if p2.isOpen():
            print('port1:Open')
        else:
            print('port1:Not Open')


if __name__ == '__main__':
    t1 = threading.Thread(target=readp1)
    t2 = threading.Thread(target=readp2)
    t3 = threading.Thread(target=writep1)
    t4 = threading.Thread(target=writep2)
    t5 = threading.Thread(target=statPort)
    t1.start()
    t2.start()
    t3.start()
    # t4.start()
    # t5.start()