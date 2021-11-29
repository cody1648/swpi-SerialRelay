# coding: UTF-8
import serial
import threading
import time

class SerialRelay:
    def __init__(self):
        try:
            # USBシリアル(SW側)
            self.port1 = serial.Serial(
                port='/dev/ttyUSB0',
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=None
            )
            # GPIOシリアル(LORAモジュール側)
            self.port2 = serial.Serial(
                port='/dev/ttyAMA0',
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=None
            )
            # 入出力バッファクリア
            self.port1.reset_input_buffer()
            self.port1.reset_output_buffer()
            self.port2.reset_input_buffer()
            self.port2.reset_output_buffer()
            time.sleep(1)

        except Exception as e:
            print(e)

    # USBシリアル->GPIOシリアル
    def relay1to2(self):
        try:
            while True:
                str = self.port1.readline()
                print('1->2:' + str.decode())
                self.port2.write(str)
        except Exception as e:
            print(e)
    # GPIOシリア->USBシリアル
    def relay2to1(self):
        try:
            while True:
                str = self.port2.readline()
                print('2->1:'+ str.decode())
                self.port1.write(str)
        except Exception as e:
            print(e)


    def write(self):
        while True:
            self.port1.write(b'\r')
            time.sleep(5)




if __name__ == '__main__':
    sr = SerialRelay()
    # USB<->GPIOどちらも受信待機できるようにスレッドを用いる
    t1 = threading.Thread(target=sr.relay1to2)
    t2 = threading.Thread(target=sr.relay2to1)
    t3 = threading.Thread(target=sr.write)
    t1.start()
    t2.start()
    t3.start()
