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
            i = 1
            while True:
                print(f'test+{i}')
                time.sleep(1)
                i += 1
        except Exception as e:
            print(e)




if __name__ == '__main__':
    sr = SerialRelay()
    thread = threading.Thread(target=sr.relay1to2)
    thread.start()
