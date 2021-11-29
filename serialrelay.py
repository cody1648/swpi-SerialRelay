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
                port='/dev/ttyAMA0',
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
        
        finally:
            self.port1.close()
            self.port2.close()

    def relay1to2(self):
        try:
            self.port1.write(b'\r')
            while True:
                print(self.port1.read_line())
                time.sleep(1)
        except Exception as e:
            print(e)




if __name__ == '__main__':
    sr = SerialRelay()
    thread = threading.Thread(target=sr.relay1to2)
    thread.start()
