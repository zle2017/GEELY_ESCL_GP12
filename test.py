import crc8
import threading, time
from collections import Counter
# coding: utf8
import sys
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex


class prpcrypt():
    def __init__(self, key):
        self.key = key
        self.mode = AES.MODE_ECB

    # 加密函数，如果text不是16的倍数【加密文本text必须为16的倍数！】，那就补足为16的倍数
    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        # 这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.目前AES-128足够用
        length = 16
        count = len(text)
        if (count % length != 0):
            add = length - (count % length)
        else:
            add = 0
        text = text #+ ('\0' * add)
        self.ciphertext = cryptor.encrypt(text)
        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串转化为16进制字符串
        return b2a_hex(self.ciphertext)

    # 解密后，去掉补足的空格用strip() 去掉
    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        plain_text = cryptor.decrypt(a2b_hex(text))
        return plain_text.rstrip(b'\0')


if __name__ == '__main__':

    pc = prpcrypt(b'\x00\x11\x22\x33\x44\x55\x66\x77\x88\x99\xaa\xbb\xcc\xdd\xee\xff')  # 初始化密钥
    e = pc.encrypt(b'\xF3\xCD\x10\xDD\x00\x11\x22\x33\x94\x25\x45\x47\x46\x4A\x5B\x7D') # ESCL
    d = pc.decrypt(e)
    print(e, d)
    e = pc.encrypt(b'\x94\x25\x45\x47\x46\x4A\x5B\x7D\x74\x03\x7B\x73\x46\xFE\x01\xEB') # PEPS
    d = pc.decrypt(e)
    print(e, d)

    seedArray = [0x25, 0x0B ,0xE3, 0x06]
    calData = [0, 0, 0, 0]
    returnKey = [0, 0, 0, 0]
    xorArray = [0xE9, 0x4A, 0x22, 0x91]

    for i in range(4):
        calData[i] = seedArray[i] ^ xorArray[i]
    returnKey[0] = ((calData[3] & 0x0F) << 4) | (calData[3] & 0xF0)
    returnKey[1] = ((calData[1] & 0x0F) << 4) | ((calData[0] & 0xF0) >> 4)
    returnKey[2] = (calData[1] & 0xF0) | (calData[2] & 0xF0) >> 4
    returnKey[3] = ((calData[0] & 0x0F) << 4) | (calData[2] & 0x0F)
    for i in range(4):
        print(hex(returnKey[i]), end=" ")
    print("")
    a = b'8c22aefb'
    print(a2b_hex(a),(a2b_hex(a)[1]))
    #assert [0x00,'"',1] == [0,34,1]
'''
hash = crc8.crc8()
hash.update(bytes([0x00,0x00,0x00,0x00,0x00,0x00,0x01]))
a = hash.digest()
y = int(a[0])^0xFF
print(hex(y),type(y))
#assert hash.hexdigest() == 'c0'
#c=b'102'
#print(type(c))
b = b'123'
#rint(b[2])

assert b'\x31\x32\x33' == b'123'


#crc=0xff
#Creat CRC8 table
for i in range(256):
    if 0 == (i%16):
        #print("\n")
        pass
    crc = i&0xFF

    #print("x:",x)
    for j in range(8):
        if crc & 0x80:
            crc = (crc << 1) ^ 0x2F
        else:
            crc = (crc << 1)
    crc &= 0xff

    #crc ^= 0xff
    #print(i)
    #print('0x%02X'%(crc),end=',')
    #crc
    #print(hex(crc),end=',')



seq = [0, 1]
def test():
    return 1

seq[0] = test()

print('seq:',seq[0])

print('hello')



asa = [0,1,0,1,0,1]
print(Counter(asa))

def fun_timer1():

    global timer1
    #重复构造定时器
    timer1 = threading.Timer(0.2,fun_timer1)
    timer1.start()
    t = time.time()
    print('hello timer_1', t)

def fun_timer():

    global timer
    #重复构造定时器
    timer = threading.Timer(0.2,fun_timer)
    timer.start()
    t = time.time()
    print('hello timer', t)
#定时调度
timer = threading.Timer(0.2,fun_timer)
timer1 = threading.Timer(0.2,fun_timer1)
timer.start()
timer1.start()
print("11111111111")

# 50秒后停止定时器
#time.sleep(1.)
#timer.cancel()
#timer1.cancel()

'''
import sys
from PyQt4 import QtCore, QtGui


class MainWindow(QtGui.QWidget):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.setWindowTitle('emit')
        self.resize(250, 150)
        #self.connect(self, QtCore.SIGNAL('closeEmitApp'), QtCore.SLOT('close()'))

        # 重新实现了keyPressEvent()事件

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_R:  # 当按下Esc键时程序就会结束
            self.close()


app = QtGui.QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec_())