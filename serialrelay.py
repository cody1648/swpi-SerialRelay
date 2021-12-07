"""
SW<--serial(1)-->raspberry pi<--LoRa(2)-->PC
本プログラムは、(1)の中継を行うためのプログラム
(2)はLRA-1評価ボードで動作するBASICプログラムが中継する(COMMコマンドを利用する予定)
"""
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

threadlock = threading.Lock()
    
class SerialRelay:
    def __init__(self):
        try:
            # USBシリアル(SW側)
            self.port0 = serial.Serial(
                port='/dev/ttyUSB0',
                baudrate=9600,#本当は115200にしたいが、SWの設定が保持できない問題がある
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=None
            )
            # USBシリアル(LORAモジュール側)
            self.port1 = serial.Serial(
                port='/dev/ttyUSB1',
                baudrate=115200,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=None
            )
            # BASICprogram実行
            self.port1.write(b'run\r\n')

            # 入出力バッファクリア
            self.port0.reset_input_buffer()
            self.port0.reset_output_buffer()
            self.port1.reset_input_buffer()
            self.port1.reset_output_buffer()
            time.sleep(1)

        except Exception as e:
            print(e)

    # USB0->USB1
    def relay0to1(self):
        try:
            while True:
                str = self.port0.readline()
                print('0->1:' + str.decode())
                threadlock.acquire()
                self.port1.write(str)
                str1 = self.port1.readline().decode()
                print("str1: " + str1)
                if b'*ok\r\n' != (str2 := self.port1.readline()):
                    print('cannot receive data correctly')
                    print(str2)
                else:
                    print("str2: " + str2.decode())
                threadlock.release()
        except Exception as e:
            print(e)

    # USB1->USB0
    def relay1to0(self):
        try:
            while True:
                str = self.port1.readline()
                print('1->0:'+ str.decode())
                self.port0.write(str+b'\r\n')
        except Exception as e:
            print(e)


    def write(self):
        while True:
            self.port0.write(b'\r')
            time.sleep(5)

    def statPort(self):
        while True:
            time.sleep(10)
            if self.port0.isOpen():
                print('port0:Open')
            else:
                print('port0:Not open')

            if self.port1.isOpen():
                print('port1:Open')
            else:
                print('port1:Not Open')

if __name__ == '__main__':
    try:
        sr = SerialRelay()
        # USB<->GPIOどちらも受信待機できるようにスレッドを用いる
        t1 = threading.Thread(target=sr.relay0to1)
        t2 = threading.Thread(target=sr.relay1to0)
        t3 = threading.Thread(target=sr.write)
        t4 = threading.Thread(target=sr.statPort)
        t1.start()
        t2.start()
        # コマンドで1が入力されたら定期的にSWに改行が送られる
        if flag:
            t3.start()
        t4.start()
    except KeyboardInterrupt as ki:
        print(ki)
    finally:
        sr.port1.write(b'end')
    

