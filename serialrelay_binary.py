# coding: UTF-8
import threading
import serial
import time
import argparse
import sys
# from serialmodules import *
from coding_module.adaptive_commandtree import adaptive_commandtree as ac
from bitarray import bitarray
from anytree import *

# コマンドラインでLoRaの設定を指定できるように
psr = argparse.ArgumentParser(
    prog = 'testserial.py',
    usage = 'unedited',
    description = '''SW<--serial(1)-->raspberry pi<--LoRa(2)-->PC
                    本プログラムは、(1)の中継を行うためのプログラム
                    (2)はLRA-1評価ボードで動作するBASICプログラムが中継する(COMMコマンドを利用する予定)'''
)
# add_argumentメソッドを使って、コマンドラインから引数を受け取る処理を作成する
psr.add_argument('--sf')
psr.add_argument('--bw', help='6(62.5kHz), 7(125kHz), 8(250kHz), 9(500kHz)')
psr.add_argument('--cr')
psr.add_argument('--ch')

args = vars(psr.parse_args())
print(args)

threadlock = threading.Lock()
# SW
p1 = serial.Serial(
                port='/dev/serial/by-id/usb-FTDI_USB_HS_SERIAL_CONVERTER_FTYIRCM8-if00-port0',
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=None
            )
# board
p2 = serial.Serial(
                port='/dev/serial/by-id/usb-Silicon_Labs_CP2102N_USB_to_UART_Bridge_Controller_0001-if00-port0',
                baudrate=115200,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=None
            )
            
p1.write(b'\r\n')
p1.write(b'end\r\n')
p1.write(b'disable\r\n')
p1.write(b'term length 0\r\n')

p2.send_break()
time.sleep(1)
# LRAの各種設定(デフォルト値としてsf/bw/cr=6/6/4)
LRAsf = args['sf'] if args['sf'] else '12'
p2.write(b'Sf=' + LRAsf.encode() + b'\r\n')
LRAbw = args['bw'] if args['bw'] in args else '8'
p2.write(b'Bw=' + LRAbw.encode() + b'\r\n')
LRAcr = args['cr'] if args['cr'] in args else '4' 
p2.write(b'Cr=' + LRAcr.encode() + b'\r\n')
LRAch = args['ch'] if args['ch'] in args else '36' 
p2.write(b'Ch=' + LRAch.encode() + b'\r\n')

# LRAmaxByte = getMaxByte_lower(int(LRAsf), int(LRAbw), int(LRAcr)) 
# if not isValidStat_lower(int(LRAsf),int(LRAbw),int(LRAcr)):
#     sys.exit(1)
# print('LRAmaxByte:'+str(LRAmaxByte))

# 16進数を用いるオプション指定
p2.write(b'comm $\r\n')
time.sleep(0.5)
p1.write(b'\r\n')
p1.reset_input_buffer()
p1.reset_output_buffer()
p2.reset_input_buffer()
p2.reset_output_buffer()

adaptive_command_tree = ac.AdaptiveCommandTree(needPadding=True)

flag = True
def serialSW():
    global flag
    while True:
        if flag:
            _str = p1.readline()
            if _str != b'\r\n':
                flag = False
            # print(_str.decode())
            response = (adaptive_command_tree.encode(_str.decode(), True).tobytes().hex() + '\r\n').encode()
            # adaptive_command_tree.updateCommandModel()            
            print(f'fromSW:{repr(_str.decode())}' + f'({len(_str)})')#for debug
            # if len(response) > LRAmaxByte:
            #     splitNum = -(- len(_str) // LRAmaxByte) - 1 #分割回数の計算
            #     print('split:'+str(splitNum))
            #     i = 0
            #     tmpStr = _str[i*LRAmaxByte:(i + 1) * LRAmaxByte]
            #     while tmpStr == '':
            #         p2.write(tmpStr + b'\r\n')
            #         i += 1
            #         tmpStr = _str[i*LRAmaxByte:(i + 1) * LRAmaxByte]
            # else:
            p2.write(response)
            _str = _str.decode()

        else:
            time.sleep(0.1)

def serialLRA():
    global flag
    while True:
        _str = p2.readline().decode()
        print(f'fromLRA:{repr(_str)}')
        if _str.startswith('@'):
            print(RenderTree(adaptive_command_tree.root))
            _str = _str.split(',')[-1].rstrip()
            tmp_bitarray = bitarray()
            tmp_bitarray.frombytes(bytes.fromhex(_str))
            print(tmp_bitarray)
            cmd = adaptive_command_tree.decode(tmp_bitarray)

            # print(cmd)
            # print(repr(cmd))
            if cmd.startswith("__CMD "):
                cmd = cmd.lstrip("__CMD ") + '\r\n'
                p1.write(cmd.encode())
            if cmd.startswith('__SYNC SEND_HASH'):
                hash_value = cmd.lstrip('__SYNC SEND_HASH ')
                if hash_value == adaptive_command_tree.hashwaitingUpdateDict().hex():
                    p2.write((adaptive_command_tree.encode('__SYNC SYNC_OK').tobytes().hex() + '\r\n').encode())
                    # waitingUpdateListからコマンドモデルを更新
                    adaptive_command_tree.updateCommandTree()
                else:
                    p2.write((adaptive_command_tree.encode('__SYNC OUT_OF_SYNC').tobytes().hex() + '\r\n').encode())
                    adaptive_command_tree.clearWaitingUpdateDict()
                
        elif _str == '*no_free_ch\r\n':
            p2.send_break()
            p2.write(b'comm $\r\n')
            flag = True
        elif _str == '*ok\r\n':
            flag = True



if __name__ == '__main__':
    t1 = threading.Thread(target=serialSW)
    t2 = threading.Thread(target=serialLRA)
    t1.start()
    t2.start()
    

