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
                timeout=1
            )
            # GPIOシリアル(LORAモジュール側)
            self.port2 = serial.Serial(
                port='/dev/serial0',
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )

            self.port1.reset_input_buffer()
            self.port1.reset_output_buffer()
            self.port2.reset_input_buffer()
            self.port2.reset_output_buffer()
            time.sleep(1)

        except Exception as e:
            print(e)


    def relay1to2(self):
        try:
            while True:
                print(self.port1.read_line())
        except Exception as e:
            print(e)

    def write(self):
        while True:
            self.port1.write(b'\r')
            time.sleep(3)




if __name__ == '__main__':
    sr = SerialRelay()
    t1 = threading.Thread(target=sr.relay1to2)
    t2 = threading.Thread(target=sr.write)
    t1.start()
    t2.start()
