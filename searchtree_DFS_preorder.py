# coding: UTF-8
from anytree import exporter
import serial
import time
import re
from anytree import *
from anytree.exporter import JsonExporter

class SearchTreeDFSPreorder:
    def __init__(self):
        pass
    #     # 正規表現コンパイル
    #     self.re1 = re.compile()
    #     self.re1 = re.compile()
    #     self.re1 = re.compile()
    #     self.re1 = re.compile()
    #     self.re1 = re.compile()
    #     self.re1 = re.compile()
    #     self.re1 = re.compile()
    #     self.re1 = re.compile()
    #     self.re1 = re.compile()
    #     self.re1 = re.compile()

    def main(self):
        startTime = time.time()
        try:
            # シリアル開通
            COM = "COM4"
            bitrate = 115200
            ser = serial.Serial(COM, bitrate, timeout = 0.1)
            ser.set_buffer_size(rx_size = 100000, tx_size = 100000)

            ser.write(b'\r')
            ser.write(b'terminal length 0\r')
            ser.reset_input_buffer()
            root = Node('root')
            self.makeCommandTree(ser, 1, root)

        # Ctrl+Cでプログラムを中断できるように
        except KeyboardInterrupt:
            print('Ctrl+Cをキャッチしました。プログラムを停止します')
        
        except Exception as e:
            print(e)

        finally:
            # シリアルクローズ
            ser.close()
            # 取得したTreeをJSONファイルにエクスポート
            exporter = JsonExporter(indent=2, sort_keys=True)
            JsonExporter.write(exporter, root, filehandle=open('cmdTree.json', 'w'))
            # 結果表示
            for pre, _ , node in RenderTree(root):
                print('%s%s' % (pre, node.name))
            print('elapsed_time:{0}'.format(time.time() - startTime) + '[sec]')


    # ser: serialのインスタンス
    # v: nodeのインスタンス
    # depth: vの深さ
    # vに引数を指定しない場合根ノードとして/rootを代入する

    # 特殊な文字列
    # <\d-\d>: そのまま
    # begin: begin以降は探索をしない
    def makeCommandTree(self, ser, depth, v):
        vName = v.name
        # プログラム実行状況を確認する用
        print('now: ' + vName + '(%s)' % depth)

        # コマンドの終端
        if vName == '<cr>':
            return
        # 正規表現指定は無限ループするため探索をしない（暫定措置2021年11月23日）
        if vName == 'begin' or vName == 'count'or vName == 'exclude' or vName == 'include':
            return
        # cryptoのEncryption指定でループするので打ち切る（暫定措置2021年11月23日）
        if vName == 'passphrase':
            return

        if v.path == 'test':
            return
        # オプション指定は複数指定できて探索にかかる時間がすごいことになるので打ち切ることもありかも？
        # if vName.startswith('-'):
        #     return

        # 探索する深さ指定
        if depth > 10:
            return

        # nodeからコマンド列を読み取る
        parentCmd = re.search(r'(?<=Node\(\').*?(?=\'\))',str(v)).group()
        parentCmd = parentCmd.split('/')[2:]
# / から始まる場合の挙動を知りたい
# 92行目：/で分割してるからそれでおかしくなっている
        flags = 0
        if len(parentCmd)>=1 and parentCmd[-1].startswith('/'):
            flags = 1

        # parent nodeに対応するコマンド解析・入力
        ser.write(b'\x15')# Ctrl+U
        time.sleep(0.1)
        ser.reset_input_buffer()# Ctrl+Uに対応するBSを無視するためのバッファクリア
        _length = len(parentCmd)
        for i, cmd in enumerate(parentCmd):
            # 数字指定の処理
            if re.match(r'<\d+-\d+>', cmd):
                # 範囲の頭の数字を代表させて入力する                                      
                ser.write(re.search(r'\d+', cmd).group().encode() + b' ')
            else:
                ser.write(cmd.encode() + b' ')
    
        vCmdList = self.getCmdList(ser, depth, flags) #list:str
        print(vCmdList[:2])
        # コマンドリストの要素を新しくノードに追加
        vChild = []
        for cmd in vCmdList:
            vChild.append(Node(cmd, v))
        # 再帰する
        for v in vChild:
            self.makeCommandTree(ser, depth+1, v)
            

    # ?を打ち込んだ時に得られるコマンドのリストを返す関数
    def getCmdList(self, ser, depth, flags=0):
        ser.reset_input_buffer()
        ser.write(b'?')
        time.sleep(0.25)
        _str = ser.read_all().decode('utf-8')
        _str = re.sub(r'.*Exec commands:\r\n',r'',_str, flags=(re.MULTILINE|re.DOTALL))
        # itijitekisyori
        if flags == 1:
            print(_str)
        p = re.compile(r'\r\n')
        _commandList = p.split(_str)
        # 最後の二つはいらないのでカット
        del _commandList[-1]
        del _commandList[-1]

        for i, cmd in enumerate(_commandList):
            cmd = re.sub('^  ','',cmd)
            cmd = re.sub(' +.*$','', cmd)
            _commandList[i] = cmd
        if '' in _commandList:
            _commandList.remove('')
        ser.reset_input_buffer()

        return _commandList[1:]

st = SearchTreeDFSPreorder()
st.main()