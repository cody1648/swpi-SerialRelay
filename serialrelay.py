# coding: UTF-8
import serial
import threading
import time
import sys

# コマンドラインでフラグ指定
flag = False
args = sys.argv
print(args)
if len(args) > 1 and args[1] == '1':
    flag = True
    
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
            # USBシリアル(LORAモジュール側)
            self.port2 = serial.Serial(
                port='/dev/ttyUSB1',
                baudrate=115200,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=None
            )
            # BASICprogram実行
            self.port2.write(b'run')

            # 入出力バッファクリア
            self.port1.reset_input_buffer()
            self.port1.reset_output_buffer()
            self.port2.reset_input_buffer()
            self.port2.reset_output_buffer()
            time.sleep(1)

        except Exception as e:
            print(e)

    # USB0->USB1
    def relay1to2(self):
        try:
            while True:
                str = self.port1.readline()
                print('1->2:' + str.decode())
                self.port2.write(str)
        except Exception as e:
            print(e)
    # USB1->USB0
    def relay2to1(self):
        try:
            while True:
                str = self.port2.readline()
                print('2->1:'+ str.decode())
                self.port1.write(str+b'\r')
        except Exception as e:
            print(e)


    def write(self):
        while True:
            self.port1.write(b'\r')
            time.sleep(5)

    def statPort(self):
        while True:
            time.sleep(10)
            if self.port1.isOpen():
                print('port1:Open')
            else:
                print('port1:Not open')

            if self.port2.isOpen():
                print('port2:Open')
            else:
                print('port2:Not Open')

if __name__ == '__main__':
    try:
        sr = SerialRelay()
        # USB<->GPIOどちらも受信待機できるようにスレッドを用いる
        t1 = threading.Thread(target=sr.relay1to2)
        t2 = threading.Thread(target=sr.relay2to1)
        t3 = threading.Thread(target=sr.write)
        t4 = threading.Thread(target=sr.statPort)
        t1.start()
        t2.start()
        # コマンドで1が入力されたら定期的にSWに改行が送られる
        if flag:
            t3.start()
    except KeyboardInterrupt as ki:
        print(ki)
    finally:
        sr.port2.write(b'end')
    

