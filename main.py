# -*- coding: utf-8 -*-

from GEELY_ESCL_GP12_Ui import Ui_MainWindow
import crc8
import sys
import threading, time
from private_method import CheckLimits, SequenceTest
from ConfigFile import Config
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from usb2pwm import *
import platform
from usb2can import *
from usb2gpio import *
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex


if (platform.system()=="Linux"):
    import RPi.GPIO as GPIO
    try:
        import RPi.GPIO
    except RuntimeError:
        print("import error!")

ESC_FrontWheelSpeedsKPH = {'ExternFlag': 0,'RemoteFlag':0, 'ID':0x1E2, 'DLC':8, 'Data':[0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]}
ESC_RearWheelSpeedsKPH  = {'ExternFlag': 0,'RemoteFlag':0, 'ID':0x122, 'DLC':8, 'Data':[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]}
EMS_EngineRPM           = {'ExternFlag': 0,'RemoteFlag':0, 'ID':0x123, 'DLC':8, 'Data':[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]}
IPK_TotalOdometer       = {'ExternFlag': 0,'RemoteFlag':0, 'ID':0x085, 'DLC':8, 'Data':[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]}
PEPS_KeyReminder_Lock   = {'ExternFlag': 0,'RemoteFlag':0, 'ID':0x27F, 'DLC':8, 'Data':[0x20, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]}
PEPS_KeyReminder_UnLock = {'ExternFlag': 0,'RemoteFlag':0, 'ID':0x27F, 'DLC':8, 'Data':[0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]}
Periodic_Msg            = {'ExternFlag': 0,'RemoteFlag':0, 'ID':0x401, 'DLC':8, 'Data':[0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]}
ESCL_DiagReq = 0x7D1
print(hex(ESC_FrontWheelSpeedsKPH['ID']),(ESC_FrontWheelSpeedsKPH['Data'][0]))

class MainUI(Ui_MainWindow, QMainWindow,QWidget,QEvent):
    test_enable = 0
    status_testing = 0

    passed = 'background-color: rgb(6, 176, 37);\ncolor: rgb(0, 0, 0);\n'
    idle = 'color: rgb(0, 0, 0)'
    hint = 'background-color: yellow;\ncolor: rgb(0, 0, 0);\n'
    failed = 'background-color: red;\ncolor: rgb(0, 0, 0);\nfont: 8pt "宋体";\n'
    testing = 'background-color: rgb(255, 255, 255);\ncolor: rgb(0, 0, 0);\nfont: 12pt "Arial";\n'
    passed_result = 'background-color: rgb(6, 176, 37);\ncolor: rgb(0, 0, 0);\nfont: 12pt "Arial";\n'
    white = 'background-color: white'

    thread_status = 0
    model = ''
    temp = 0
    config_ESCL = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    test_button = 0
    test_button_status = 0
    btn_light_status = [0, 0]
    btn_pad_status = [0, 0]
    btn_pad_on = [0, 0]
    btn_pad_off = [0, 0]
    btn_on_01 = [0, 0]
    btn_off_01 = [0, 0]
    count = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    fl_fr_hs_mark = [0, 0]
    count_test_enable = 0
    day_night_mark = 1
    _btn_start = 0
    count_btn_start = 0
    hsw_mark = 0
    pam_01 = [0, 0]
    pam_on_off = [0, 0]
    pam_mark = 0
    value_hzw_res = 9999.0
    res_hzw = 999
    hzw_count = 0
    _temp = [0, 0]
    rpi_GPIO = [0, 0, 0, 0]
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        super(MainUI, self).__init__(parent)
        #self.teststart.

        self.setupUi(self)
        self.thread = Worker()
        self.thread.start()
        self.config = Config()
        self.check_limits = CheckLimits()
        self.SequenceTest = SequenceTest()
        self.thread.finished.connect(self.thread_control)
        self.model_select.currentIndexChanged.connect(self.exec_config)
        self.teststart.clicked.connect(self.exec_start)
        self.thread.dataSignal.connect(self.exec_function_check)
        self.pushButton.clicked.connect(self.exec_bolt_unlock_lock)
        self.pushButton_2.clicked.connect(self.exec_clear_DTC)
        self.radioButton_2.clicked.connect(self.SetBTNText)
        self.radioButton.clicked.connect(self.SetBTNText)
        self.side_select.setVisible(False)
        self.tableWidget.setColumnWidth(0, 300)
        self.tableWidget.setDisabled(True)
        #

        #self.exec_config()
        if self.thread.usb2xxx_load_mark == 0:
            QMessageBox.warning(self,"Warning","Can't found USB2XXX! Please check Device!", QMessageBox.Ok)
            self.frame.setStyleSheet(self.hint)
            self.label_5.setVisible(True)
            self.label_5.setText("Device fault !!!")
        else:
            self.label_5.setVisible(False)
        self.exec_product_select()
        self.exec_init()



    def keyPressEvent(self, event):
        #if event.modifiers() == Qt.ControlModifier:
        #self.event(QEvent)
        #QKeyEventTransition.setKey(Qt.DownArrow)
        #test = QKeyEventTransition()
        #test.setKey(QKeyEvent.Shortcut)

        #test.onTransition()

        if event.key() == Qt.Key_M:  # 当按下Esc键时程序就会结束

            self.ComboboxPopUp()
            print("key = M")

        if event.key() == Qt.Key_U:
            print("key = U")
            self.model_select.setCurrentIndex(3)
            self.ComboboxPopUp()
        #if self.pushButton_3.setShortcut
        
     
    def select_model_disable(self):
        self.model_select.setEnabled(False)
        self.exec_init()

    def thread_wait(self):
        if self.side_select.isVisible:
            self.thread_status = 1
        else:
            pass

    def thread_control(self):
        if self.thread_status == 0:
            self.thread.start()
        else:
            pass


    def exec_start(self):
        self.thread.TestStatus = 0
        self.thread.testTimer.start()
        print("starting~~~~~")
        self.thread.data_init()
        self.SequenceTest.init()
        self.thread_status = 1
        self.thread.response_selector = 1
        self.exec_init()
        if self.status_testing == 0:
            self.exec_init()
            # self.result_txt_line.setStyleSheet(self.testing)
            self.test_enable = 1
            self.result_txt_line.setText('Testing......')
            self.result_txt_line.setStyleSheet(self.testing)
        self.thread_status = 0

    def exec_reset(self):

        self.test_enable = 0
        self.status_testing = 0
        self.exec_init()
        self.thread_status = 0
        # self.result_txt_line.clear()
        self.thread.start()

    def select_model_enable(self):
        self.model_select.setEnabled(True)

    def exec_product_select(self):

        side = self.side_select.currentText()
        if side == 'GEELY':
            self.model_select.clear()
            self.config.file_dir = 'TestConfig/'
            self.model_select.addItems(self.config.get_list())
            self.thread_status = 0
            self.thread.start()

    def show_time(self):
        self.time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    def ComboboxPopUp(self):
        self.model_select.showPopup()
    def SetBTNText(self):
        pass
    def exec_function_check(self, product_info, lin_data):

        #QKeyEventTransition.onTransition()
        if product_info['7107'] == '00':
            self.pushButton.setText("Lock")
        if product_info['7107'] == '01':
            self.pushButton.setText('UnLock')
            #self.pushButton.setStyleSheet("font:Arial 10px;")
        self.RpiBTN()
        if self.thread.count_mark == 1:
            if self.config_ESCL[7] == 1:
                self.tableWidget.setItem(0, 1, QTableWidgetItem(product_info['F180']))
        if self.thread.count_mark == 2:
            if self.config_ESCL[8] == 1:
                self.tableWidget.setItem(1, 1, QTableWidgetItem(product_info['F18C']))
        if self.thread.count_mark == 3:
            if self.config_ESCL[9] == 1:
                self.tableWidget.setItem(2, 1, QTableWidgetItem(product_info['F193']))
        if self.thread.count_mark == 4:
            if self.config_ESCL[2] == 1:
                self.tableWidget.setItem(3, 1, QTableWidgetItem(product_info['F195']))
                if self.radioButton.isChecked():
                    if product_info['F195'] != self.config_ESCL[1]:
                        self.tableWidget.item(3, 1).setBackground(QBrush(QColor(255, 0, 0)))
        if self.thread.count_mark == 5:
            if self.config_ESCL[4] == 1:
                self.tableWidget.setItem(4, 1, QTableWidgetItem(product_info['F187']))
                if self.radioButton.isChecked():
                    if product_info['F187'] != self.config_ESCL[3]:
                        self.tableWidget.item(4, 1).setBackground(QBrush(QColor(255, 0, 0)))
        if self.thread.count_mark == 6:
            if self.config_ESCL[6] == 1:
                self.tableWidget.setItem(5, 1, QTableWidgetItem(product_info['F18A']))
                if self.radioButton.isChecked():
                    if product_info['F18A'] != self.config_ESCL[5]:
                        self.tableWidget.item(5, 1).setBackground(QBrush(QColor(255, 0, 0)))
        if self.thread.count_mark == 7:
            if self.config_ESCL[10] == 1:
                self.tableWidget.setItem(6, 1, QTableWidgetItem(product_info['F18B']))

        if self.radioButton.isChecked():
            self.thread.TestModel = 1
            if self.thread.count_mark == 12:
                self.exec_bolt_unlock_lock()
                self.exec_pass()
        if self.radioButton_2.isChecked():
            self.thread.TestModel = 0
            self.result_txt_line.setText('')
            self.result_txt_line.setStyleSheet(self.white)
        self.tableWidget.setItem(7, 1, QTableWidgetItem(product_info['7109']))
        self.tableWidget.setItem(8, 1, QTableWidgetItem(product_info['7107']))
        self.tableWidget.setItem(9, 1, QTableWidgetItem(lin_data))

        #print(self.pushButton.isChecked)



        #self.info_table.setItem(3, 6, QTableWidgetItem('Pass'))
        #print(product_info)
        btn_start = 1 if self.count_btn_start > 1 else 0
        if (btn_start ^ self._btn_start) & btn_start:
            self.exec_start()
            self.count_test_enable = 0
            self.count_btn_start = 0
        self._btn_start = btn_start

        self.exec_sequence_test( product_info, lin_data)


    def exec_sequence_test(self, product_info, lin_data):

        # if self.side_select.currentText() == 'Audi':
        if 1:
           # self.test_button = 1 if ~di_data[1] & 128 else 0
            #if (self.test_button ^ self.test_button_status) & self.test_button:
                #self.exec_start()
            #self.test_button_status = self.test_button
            if self.test_enable:
                pass
                # self.thread.response_selector = 1




    def RpiBTN(self):
        if (platform.system() == "Linux"):
            rpiBTN33 = 1 if (RPi.GPIO.input(33)) == 0 else 0
            if (rpiBTN33 ^ self.rpi_GPIO[0]) & rpiBTN33:
                if self.model_select.currentIndex() != (self.model_select.count() - 1):
                    self.model_select.setCurrentIndex(self.model_select.currentIndex() + 1)
                else:
                    self.model_select.setCurrentIndex(0)
                print('in33--------------------------------')
            self.rpi_GPIO[0] = rpiBTN33

            rpiBTN34 = 1 if (RPi.GPIO.input(34)) == 0 else 0
            if (rpiBTN34 ^ self.rpi_GPIO[1]) & rpiBTN34:
                if self.radioButton.isChecked():
                    self.radioButton_2.setChecked(True)
                elif self.radioButton_2.isChecked():
                    self.radioButton.setChecked(True)

            self.rpi_GPIO[1] = rpiBTN34

            if (RPi.GPIO.input(35)) == 0: print("35  = True")
            if (RPi.GPIO.input(36)) == 0: print("36  = True")

    def exec_pass(self):
        self.result_txt_line.setStyleSheet(self.passed_result)
        self.result_txt_line.setText('Passed')
        self.test_enable = 0
        self.status_testing = 0
        self.model_select.setEnabled(True)
        self.side_select.setEnabled(True)
        self.side_select.setEnabled(True)
        print(self.thread.testTimer.isActive())
        self.thread.testTimer.stop()
        self.thread.TestStatus = 1

    def exec_fail(self):
        self.test_enable = 0
        self.status_testing = 0
        self.result_txt_line.setStyleSheet(self.failed)
        self.result_txt_line.setText('Failed')

    def exec_bolt_unlock_lock(self):
        self.thread.count_mark = 25
        self.thread.mark = 1
    def exec_clear_DTC(self):
        self.thread.mark_1 = 1
        self.thread.count_mark = 7
        self.thread.clear_DTC_mark = 1
    def exec_init(self):
        if (platform.system() == "Linux"):
            RPi.GPIO.setmode(RPi.GPIO.BCM)
            RPi.GPIO.setup(33, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP)
            RPi.GPIO.setup(34, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP)
            RPi.GPIO.setup(35, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP)
            RPi.GPIO.setup(36, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP)

        if self.config_ESCL[7] == 1:
            self.tableWidget.setItem(0, 0, QTableWidgetItem("F180:  Boot Software Identification"))
        else:
            self.tableWidget.setItem(0, 0, QTableWidgetItem(""))
        if self.config_ESCL[8] == 1:
            self.tableWidget.setItem(1, 0, QTableWidgetItem("F18C:  ECU Serial Number"))
        else:
            self.tableWidget.setItem(1, 0, QTableWidgetItem(""))
        if self.config_ESCL[9] == 1:
            self.tableWidget.setItem(2, 0, QTableWidgetItem("F193:  System Supplier ECU HW Version Number"))
        else:
            self.tableWidget.setItem(2, 0, QTableWidgetItem(""))

        if self.config_ESCL[2] == 1:
            self.tableWidget.setItem(3, 0, QTableWidgetItem("F195:  System Supplier ECU SW Version Number"))
        else:
            self.tableWidget.setItem(3, 0, QTableWidgetItem(""))

        if self.config_ESCL[4] == 1:
            self.tableWidget.setItem(4, 0, QTableWidgetItem("F187:  Geely Spare Part Number"))
        else:
            self.tableWidget.setItem(4, 0, QTableWidgetItem(""))

        if self.config_ESCL[6] == 1:
            self.tableWidget.setItem(5, 0, QTableWidgetItem("F18A:  System Supplier Identifier"))
        else:
            self.tableWidget.setItem(5, 0, QTableWidgetItem(""))

        if self.config_ESCL[10] == 1:
            self.tableWidget.setItem(6, 0, QTableWidgetItem("F18B:  ECU Manufacturing Date"))
        else:
            self.tableWidget.setItem(6, 0, QTableWidgetItem(""))
        self.tableWidget.setItem(7, 0, QTableWidgetItem("7109:  ESCL_Learning_Status"))
        self.tableWidget.setItem(8, 0, QTableWidgetItem("7107:  ESCL_Steering Lock Status"))
        self.tableWidget.setItem(9, 0, QTableWidgetItem("0279:  ESCL_Message_Info"))
        self.thread.mark = 1
        self.thread.mark_1 = 1
        self.thread.write_sk128_mark = 0
        while self.thread.count_mark > 10:
            self.thread.clear_DTC_mark = 0
            self.thread.product_info['F180'] = ''
            self.thread.product_info['F18C'] = ''
            self.thread.product_info['F193'] = ''
            self.thread.product_info['F195'] = ''
            self.thread.product_info['F187'] = ''
            self.thread.product_info['F18A'] = ''
            self.thread.product_info['F18B'] = ''
            #self.thread.product_info['7109'] = ''
            #self.thread.product_info['7107'] = ''

            self.tableWidget.setItem(0, 1, QTableWidgetItem(''))

            self.tableWidget.setItem(1, 1, QTableWidgetItem(''))
            self.tableWidget.setItem(2, 1, QTableWidgetItem(''))
            self.tableWidget.setItem(3, 1, QTableWidgetItem(''))
            self.tableWidget.setItem(4, 1, QTableWidgetItem(''))
            self.tableWidget.setItem(5, 1, QTableWidgetItem(''))
            self.tableWidget.setItem(6, 1, QTableWidgetItem(''))
            self.tableWidget.setItem(7, 1, QTableWidgetItem(''))
            self.tableWidget.setItem(8, 1, QTableWidgetItem(''))

            self.thread.count_mark = 0
        self.SequenceTest.number_count = 2


    def exec_config(self):
        try:
            if self.side_select.currentText() == 'GEELY':
                self.config.file_dir = 'TestConfig/'
                value_dict = self.config.get_value(self.model_select.currentText())
                if self.model_select.count() > 0:
                    #print((value_dict.get('TimeOut'))['Time'])
                    self.config_ESCL[0] =  int((value_dict.get('Timeout'))['Time'])
                    self.config_ESCL[1] =  str((value_dict.get('F195'))['SWVersionNumber'])
                    self.config_ESCL[2] =  int((value_dict.get('F195'))['Enable'])
                    self.config_ESCL[3] =  str((value_dict.get('F187'))['PartNumber'])
                    self.config_ESCL[4] =  int((value_dict.get('F187'))['Enable'])
                    self.config_ESCL[5] =  str((value_dict.get('F18A'))['SystemSupplierID'])
                    self.config_ESCL[6] =  int((value_dict.get('F18A'))['Enable'])
                    self.config_ESCL[7] =  int((value_dict.get('F180'))['Enable'])
                    self.config_ESCL[8] =  int((value_dict.get('F18C'))['Enable'])
                    self.config_ESCL[9] =  int((value_dict.get('F193'))['Enable'])
                    self.config_ESCL[10] = int((value_dict.get('F18B'))['Enable'])
                print(self.config_ESCL)
        except:
            QMessageBox.warning(self,"Warning","Can't load configfile! Please check this Configfile!",
                                      QMessageBox.Ok)
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

class MyException(Exception):
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message

class Worker(QThread):
    Cal_Key_Value = list(range(8))
    temp_msg = [0, 0, 0, 0, 0, 0, 0]
    temp_msg1 = [0, 0, 0, 0, 0, 0, 0]
    mark = 0
    mark_1 = 0
    clear_DTC_mark = 0
    last_count_0 = 0
    last_count_1 = 0
    last_count_2 = 0
    last_count_3 = 0
    last_count_4 = 0
    last_count_5 = 0
    last_count_6 = 0
    last_count_7 = 0
    last_status = 0
    last_gpio_WT_data = 0x000
    count = 0
    write_sk128_mark = 0
    count_peps = 0
    count_EMS_EngineRPM = 0
    dataSignal = pyqtSignal(dict, str)
    timerCount = 0
    EROcount = 0
    count_Periodic = 0
    count_mark = 28
    countGet = 0
    response_selector = 0
    product_info = {'F180' : '', 'F187' : '', 'F18A' : '', 'F18B' : '', 'F18C' : '',
                    'F193' : '', 'F195' : '', '7107' : '', '7109' : ''}
    lin_data = [0, 0, 0, 0, 0, 0, 0, 0]
    _response = ''
    CANIndex = 0
    DevHandles = (c_uint * 20)()
    timerMark = 0
    _timerMark = 0
    testTimer = None
    DiagReq_Enable = 0
    no_msg_count = 0
    access_mark = 0
    usb2xxx_load_mark = 1
    TestStatus = 0
    TestModel = 1
    def __init__(self, parent=None):
        super(Worker, self).__init__(parent)
        self.working = True
        # Scan device
        #try:
        ret = USB_ScanDevice(byref(self.DevHandles))
        if (ret == 0):
            print("No device connected!")
            self.usb2xxx_load_mark = 0
        else:
            print("Have %d device connected!" % ret)
        # Open device
        ret = USB_OpenDevice(self.DevHandles[0])
        if (bool(ret)):
            print("Open device success!")
        else:
            print("Open device faild!")
            #exit()
        self.Cal_Key([0x00, 0x00, 0x00, 0x25, 0x0B, 0xE3, 0x06, 0x00])
        # Get device infomation
        try:
            USB2XXXInfo = DEVICE_INFO()
            USB2XXXFunctionString = (c_char * 256)()
            ret = DEV_GetDeviceInfo(self.DevHandles[0], byref(USB2XXXInfo), byref(USB2XXXFunctionString))
            if (bool(ret)):
                print("USB2XXX device infomation:")
                print("--Firmware Name: %s" % bytes(USB2XXXInfo.FirmwareName).decode('ascii'))
                print("--Firmware Version: v%d.%d.%d" % (
                (USB2XXXInfo.FirmwareVersion >> 24) & 0xFF, (USB2XXXInfo.FirmwareVersion >> 16) & 0xFF,
                USB2XXXInfo.FirmwareVersion & 0xFFFF))
                print("--Hardware Version: v%d.%d.%d" % (
                (USB2XXXInfo.HardwareVersion >> 24) & 0xFF, (USB2XXXInfo.HardwareVersion >> 16) & 0xFF,
                USB2XXXInfo.HardwareVersion & 0xFFFF))
                print("--Build Date: %s" % bytes(USB2XXXInfo.BuildDate).decode('ascii'))
                print("--Serial Number: ", end='')
                for i in range(0, len(USB2XXXInfo.SerialNumber)):
                    print("%08X" % USB2XXXInfo.SerialNumber[i], end='')
                print("")
                print("--Function String: %s" % bytes(USB2XXXFunctionString.value).decode('ascii'))
            else:
                print("Get device infomation faild!")
                #exit()
            # 初始化CAN
            CANConfig = CAN_INIT_CONFIG()
            CANConfig.CAN_Mode = 0  # 1-自发自收模式，0-正常模式
            CANConfig.CAN_ABOM = 0
            CANConfig.CAN_NART = 1
            CANConfig.CAN_RFLM = 0
            CANConfig.CAN_TXFP = 1
            # 配置波特率,波特率 = 100M/(BRP*(SJW+BS1+BS2))
            CANConfig.CAN_BRP_CFG3 = 25
            CANConfig.CAN_BS1_CFG1 = 6
            CANConfig.CAN_BS2_CFG2 = 1
            CANConfig.CAN_SJW = 1
            ret = CAN_Init(self.DevHandles[0], self.CANIndex, byref(CANConfig))
            if (ret != CAN_SUCCESS):
                print("Config CAN failed!")
                #exit()
            else:
                print("Config CAN Success!")
            # 配置过滤器，必须配置，否则可能无法收到数据
            CANFilter = CAN_FILTER_CONFIG()
            CANFilter.Enable = 1
            CANFilter.ExtFrame = 0
            CANFilter.FilterIndex = 0
            CANFilter.FilterMode = 0
            CANFilter.MASK_IDE = 0
            CANFilter.MASK_RTR = 0
            CANFilter.MASK_Std_Ext = 0
            ret = CAN_Filter_Init(self.DevHandles[0], self.CANIndex, byref(CANFilter))
            if (ret != CAN_SUCCESS):
                print("Config CAN Filter failed!")
                #exit()
            else:
                print("Config CAN Filter Success!")

            self.time()
            GPIO_SetOutput(self.DevHandles[0], 0x200, 1)
            #GPIO_SetOutput(self.DevHandles[0], 0x100, 1)
            #GPIO_SetOutput(self.DevHandles[0], 0x200, 1)
            #GPIO_Write(self.DevHandles[0], 0x100, 0x100)

            PWMConfig = PWM_CONFIG()
            PWMConfig.ChannelMask = 0x08  # 初始化所有通道
            PWMConfig.Polarity[3] = 0  # 将所有PWM通道都设置为正极性
            PWMConfig.Precision[3] = 100  # 将所有通道的占空比调节精度都设置为1%
            PWMConfig.Prescaler[3] = 1  # 将所有通道的预分频器都设置为10，则PWM输出频率为200MHz/(PWMConfig.Precision*PWMConfig.Prescaler)
            PWMConfig.Pulse[3] = PWMConfig.Precision[3] * 30 // 100  # 将所有通道的占空比都设置为30%
            # 初始化PWM
            ret = PWM_Init(self.DevHandles[0], byref(PWMConfig))
            if ret != PWM_SUCCESS:
                print("Initialize pwm faild!")
                #exit()
            else:
                print("Initialize pwm sunccess!")
            # 启动PWM,RunTimeOfUs之后自动停止，利用该特性可以控制输出脉冲个数，脉冲个数=RunTimeOfUs*200/(PWMConfig.Precision*PWMConfig.Prescaler)
            RunTimeOfUs = 0
            ret = PWM_Start(self.DevHandles[0], PWMConfig.ChannelMask, RunTimeOfUs)
            if (ret != PWM_SUCCESS):
                print("Start pwm faild!")
                #exit()
            else:
                print("Start pwm sunccess!")
        except:
            pass

    def __del__(self):
        self.working = False
        self.wait()
    def data_init(self):
        pass
        # self.response_selector = 0
    def chr_load(self, int_byte):
        if int_byte < 10 or int_byte == 0:
            temp1 = (hex(int_byte)).upper()
            temp2 = ('0') + temp1[2:]
            return temp2
        else:
            temp1 = (hex(int_byte)).upper()
            temp2 = temp1[2:]
            return temp2
    def SendPeriodic_Msg(self):
        CanMsg = (CAN_MSG * 1)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x401
        CanMsg[0].DataLen = 8
        CanMsg[0].Data[0] = 0xFF
        CanMsg[0].Data[1] = 0xFF
        for i in range(0, 6):
            CanMsg[0].Data[i + 2] = 0x00

        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 1)
        t = time.time()
        #print('hello timer_2', t)
    def SendPeriodic_Msg_20ms(self):
        CanMsg = (CAN_MSG * 3)()
        for i in range(3):
            CanMsg[i].ExternFlag = 0
            CanMsg[i].RemoteFlag = 0
            CanMsg[i].DataLen = 8
        CanMsg[0].ID = 0x1E2
        CanMsg[1].ID = 0x122
        CanMsg[2].ID = 0x123
        CanMsg[0].Data[0] = 0x02
        CanMsg[1].Data[0] = 0x00
        CanMsg[2].Data[0] = 0x00
        for i in range(0, 5):
            CanMsg[0].Data[i + 1] = 0x00
        if self.count_peps < 15:
            self.count_peps += 1
            for j in range(3):
                CanMsg[j].Data[6] = self.count_peps
                for k in range(7):
                    self.temp_msg[k] = CanMsg[j].Data[k]
                hash = crc8.crc8()
                hash.update(bytes(self.temp_msg))
                CanMsg[j].Data[7] = int(hash.digest()[0]) ^ 0xFF
        else:
            self.count_peps = 0
        '''
        for i in range(3):
            print(("%04X " % CanMsg[i].ID), ' ', end='')
            for j in range(0, CanMsg[i].DataLen):
                print("%02X " % CanMsg[i].Data[j], end='')
            print("")
        '''
        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 3)

        t = time.time()
        #print('hello timer_2', t)
    def SendPeriodic_Msg_10ms(self):
        CanMsg = (CAN_MSG * 2)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].DataLen = 8
        CanMsg[0].ID = 0x085
        CanMsg[0].Data[0] = 0x00
        CanMsg[0].Data[1] = 0x00
        CanMsg[0].Data[2] = 0x00
        CanMsg[0].Data[3] = 0x00
        CanMsg[0].Data[5] = 0x00
        CanMsg[0].Data[6] = 0x00
        if self.count_EMS_EngineRPM < 0xF0:
            self.count_EMS_EngineRPM += 16
            CanMsg[0].Data[7] = self.count_EMS_EngineRPM
            for k in range(4):
                self.temp_msg1[k] = CanMsg[0].Data[k]
            self.temp_msg1[4] = CanMsg[0].Data[5]
            self.temp_msg1[5] = CanMsg[0].Data[6]
            self.temp_msg1[6] = CanMsg[0].Data[7]
            hash = crc8.crc8()
            hash.update(bytes(self.temp_msg1))
            CanMsg[0].Data[4] = int(hash.digest()[0]) ^ 0xFF
        else:
            self.count_EMS_EngineRPM = 0
        '''
        #SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 1)
        CanMsg[1].ExternFlag = 0
        CanMsg[1].RemoteFlag = 0
        CanMsg[1].DataLen = 8
        CanMsg[1].ID = 0x285
        CanMsg[1].Data[0] = 0x00
        CanMsg[1].Data[1] = 0x00
        CanMsg[1].Data[2] = 0x00
        CanMsg[1].Data[3] = 0x00
        CanMsg[1].Data[4] = 0x00
        CanMsg[1].Data[5] = 0x00
        CanMsg[1].Data[6] = 0x00
        CanMsg[1].Data[7] = 0x00
        
        t = time.time()
        for i in range(1):
            print(("%04X " % CanMsg[i].ID), ' ', end='')
        for j in range(0, CanMsg[i].DataLen):
            print("%02X " % CanMsg[i].Data[j], end='')
        print("")
            #print(t)
        '''
        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 1)
        if SendedNum >= 0:
            pass
            #print("Success send frames:%d" % SendedNum)

        #print('hello timer_2', t)
    def SendPeriodic_Msg_100ms(self):
        CanMsg = (CAN_MSG * 2)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x3F1
        CanMsg[0].DataLen = 8
        for i in range(0, 8):
            CanMsg[0].Data[i] = 0x00
        CanMsg[1].ExternFlag = 0
        CanMsg[1].RemoteFlag = 0
        CanMsg[1].ID = 0x285
        CanMsg[1].DataLen = 8
        for i in range(8):
            CanMsg[1].Data[i] = 0x00

        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 2)
    def GetF180(self):
        CanMsg = (CAN_MSG * 1)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x7D1
        CanMsg[0].DataLen = 8
        CanMsg[0].Data[0] = 0x03
        CanMsg[0].Data[1] = 0x22
        CanMsg[0].Data[2] = 0xF1
        CanMsg[0].Data[3] = 0x80


        for i_1 in range(0, 4):
            CanMsg[0].Data[i_1 + 4] = 0x00
        for i in range(0, 4):
            CanMsg[0].Data[i + 4] = 0x00
        t = time.time()
        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 1)

        CanMsg = (CAN_MSG * 1)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x7D1
        CanMsg[0].DataLen = 8
        CanMsg[0].Data[0] = 0x30
        CanMsg[0].Data[1] = 0x00
        CanMsg[0].Data[2] = 0x0A

        for i in range(0, 5):
            CanMsg[0].Data[i + 3] = 0x00

        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 1)
    def GetF18C(self):
        CanMsg = (CAN_MSG * 2)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x7D1
        CanMsg[0].DataLen = 8
        CanMsg[0].Data[0] = 0x03
        CanMsg[0].Data[1] = 0x22
        CanMsg[0].Data[2] = 0xF1
        CanMsg[0].Data[3] = 0x8C
        for i in range(0, 4):
            CanMsg[0].Data[i + 4] = 0x00
        for i in range(0, 4):
            CanMsg[0].Data[i + 4] = 0x00

        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 1)

        CanMsg = (CAN_MSG * 1)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x7D1
        CanMsg[0].DataLen = 8
        CanMsg[0].Data[0] = 0x30
        CanMsg[0].Data[1] = 0x00
        CanMsg[0].Data[2] = 0x0A

        for i in range(0, 5):
            CanMsg[0].Data[i + 3] = 0x00

        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 1)
    def GetF193(self):
        CanMsg = (CAN_MSG * 1)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x7D1
        CanMsg[0].DataLen = 8
        CanMsg[0].Data[0] = 0x03
        CanMsg[0].Data[1] = 0x22
        CanMsg[0].Data[2] = 0xF1
        CanMsg[0].Data[3] = 0x93


        for i in range(0, 4):
            CanMsg[0].Data[i + 4] = 0x00
        for i in range(0, 4):
            CanMsg[0].Data[i + 4] = 0x00
        t = time.time()
        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 1)

        CanMsg = (CAN_MSG * 1)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x7D1
        CanMsg[0].DataLen = 8
        CanMsg[0].Data[0] = 0x30
        CanMsg[0].Data[1] = 0x00
        CanMsg[0].Data[2] = 0x0A

        for i in range(0, 5):
            CanMsg[0].Data[i + 3] = 0x00
        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 1)
    def GetF195(self):
        CanMsg = (CAN_MSG * 1)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x7D1
        CanMsg[0].DataLen = 8
        CanMsg[0].Data[0] = 0x03
        CanMsg[0].Data[1] = 0x22
        CanMsg[0].Data[2] = 0xF1
        CanMsg[0].Data[3] = 0x95
        for i in range(0, 4):
            CanMsg[0].Data[i + 4] = 0x00
        for i in range(0, 4):
            CanMsg[0].Data[i + 4] = 0x00
        t = time.time()
        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 1)

        CanMsg = (CAN_MSG * 1)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x7D1
        CanMsg[0].DataLen = 8
        CanMsg[0].Data[0] = 0x30
        CanMsg[0].Data[1] = 0x00
        CanMsg[0].Data[2] = 0x0A

        for i in range(0, 5):
            CanMsg[0].Data[i + 3] = 0x00

        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 1)
    def GetF187(self):
        CanMsg = (CAN_MSG * 1)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x7D1
        CanMsg[0].DataLen = 8
        CanMsg[0].Data[0] = 0x03
        CanMsg[0].Data[1] = 0x22
        CanMsg[0].Data[2] = 0xF1
        CanMsg[0].Data[3] = 0x87
        for i in range(0, 4):
            CanMsg[0].Data[i + 4] = 0x00
        for i in range(0, 4):
            CanMsg[0].Data[i + 4] = 0x00
        t = time.time()
        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 1)

        CanMsg = (CAN_MSG * 1)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x7D1
        CanMsg[0].DataLen = 8
        CanMsg[0].Data[0] = 0x30
        CanMsg[0].Data[1] = 0x00
        CanMsg[0].Data[2] = 0x0A

        for i in range(0, 5):
            CanMsg[0].Data[i + 3] = 0x00

        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 1)
    def GetF18A(self):
        CanMsg = (CAN_MSG * 1)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x7D1
        CanMsg[0].DataLen = 8
        CanMsg[0].Data[0] = 0x03
        CanMsg[0].Data[1] = 0x22
        CanMsg[0].Data[2] = 0xF1
        CanMsg[0].Data[3] = 0x8A
        for i in range(0, 4):
            CanMsg[0].Data[i + 4] = 0x00
        for i in range(0, 4):
            CanMsg[0].Data[i + 4] = 0x00
        t = time.time()
        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 1)

        CanMsg = (CAN_MSG * 1)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x7D1
        CanMsg[0].DataLen = 8
        CanMsg[0].Data[0] = 0x30
        CanMsg[0].Data[1] = 0x00
        CanMsg[0].Data[2] = 0x0A

        for i in range(0, 5):
            CanMsg[0].Data[i + 3] = 0x00

        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 1)
    def GetF18B(self):
        CanMsg = (CAN_MSG * 1)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x7D1
        CanMsg[0].DataLen = 8
        CanMsg[0].Data[0] = 0x03
        CanMsg[0].Data[1] = 0x22
        CanMsg[0].Data[2] = 0xF1
        CanMsg[0].Data[3] = 0x8B
        for i in range(0, 4):
            CanMsg[0].Data[i + 4] = 0x00
        for i in range(0, 4):
            CanMsg[0].Data[i + 4] = 0x00
        t = time.time()
        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 1)
    def Get7109(self):
        CanMsg = (CAN_MSG * 1)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x7D1
        CanMsg[0].DataLen = 8
        CanMsg[0].Data[0] = 0x03
        CanMsg[0].Data[1] = 0x22
        CanMsg[0].Data[2] = 0x71
        CanMsg[0].Data[3] = 0x09
        for i in range(0, 4):
            CanMsg[0].Data[i + 4] = 0x00
        for i in range(0, 4):
            CanMsg[0].Data[i + 4] = 0x00
        t = time.time()
        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 1)
    def Get7107(self):
        CanMsg = (CAN_MSG * 1)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x7D1
        CanMsg[0].DataLen = 8
        CanMsg[0].Data[0] = 0x03
        CanMsg[0].Data[1] = 0x22
        CanMsg[0].Data[2] = 0x71
        CanMsg[0].Data[3] = 0x07
        for i in range(0, 4):
            CanMsg[0].Data[i + 4] = 0x00
        for i in range(0, 4):
            CanMsg[0].Data[i + 4] = 0x00
        t = time.time()
        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 1)
    def UnLock(self):
        CanMsg = (CAN_MSG * 1)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x27F
        CanMsg[0].DataLen = 8
        CanMsg[0].Data[0] = 0x00
        CanMsg[0].Data[1] = 0x08
        CanMsg[0].Data[2] = 0x00
        CanMsg[0].Data[3] = 0x00
        CanMsg[0].Data[4] = 0x00
        CanMsg[0].Data[5] = 0x00
        CanMsg[0].Data[6] = 0x00
        CanMsg[0].Data[7] = 0x00

        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 1)
        #print("`````````````````````````````````")
    def Lock(self):
        CanMsg = (CAN_MSG * 1)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x27F
        CanMsg[0].DataLen = 8
        CanMsg[0].Data[0] = 0x20
        CanMsg[0].Data[1] = 0x00
        CanMsg[0].Data[2] = 0x00
        CanMsg[0].Data[3] = 0x00
        CanMsg[0].Data[4] = 0x00
        CanMsg[0].Data[5] = 0x00
        CanMsg[0].Data[6] = 0x00
        CanMsg[0].Data[7] = 0x00
        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 1)
        if SendedNum >= 0:
            pass
            #print("Success send frames:%d" % SendedNum)
        #print("bolt lock")
        #print("%04X " % CanMsg[0].ID, end='')
        #for j in range(0, CanMsg[0].DataLen):
            #print("%02X " % CanMsg[0].Data[j], end='')
        #print("")
    def SetLaernStatus(self):
        CanMsg = (CAN_MSG * 1)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x7D1
        CanMsg[0].DataLen = 8
        CanMsg[0].Data[0] = 0x07
        CanMsg[0].Data[1] = 0x2E
        CanMsg[0].Data[2] = 0xFD
        CanMsg[0].Data[3] = 0x00
        CanMsg[0].Data[4] = 0x02
        CanMsg[0].Data[5] = 0x00
        CanMsg[0].Data[6] = 0x00
        CanMsg[0].Data[7] = 0x00
        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 1)
    def WriteSK128_0(self):
        CanMsg = (CAN_MSG * 1)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x7D1
        CanMsg[0].DataLen = 8
        CanMsg[0].Data[0] = 0x10
        CanMsg[0].Data[1] = 0x13
        CanMsg[0].Data[2] = 0x2E
        CanMsg[0].Data[3] = 0x71
        CanMsg[0].Data[4] = 0x30
        CanMsg[0].Data[5] = 0x00
        CanMsg[0].Data[6] = 0x11
        CanMsg[0].Data[7] = 0x22

        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 1)
        if SendedNum >= 0:
            pass
            #print("Write SK128_0 Success send frames:%d" % SendedNum)
    def WriteSK128_1(self):
        CanMsg = (CAN_MSG * 2)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x7D1
        CanMsg[0].DataLen = 8
        CanMsg[0].Data[0] = 0x21
        CanMsg[0].Data[1] = 0x33
        CanMsg[0].Data[2] = 0x44
        CanMsg[0].Data[3] = 0x55
        CanMsg[0].Data[4] = 0x66
        CanMsg[0].Data[5] = 0x77
        CanMsg[0].Data[6] = 0x88
        CanMsg[0].Data[7] = 0x99
        CanMsg[1].ExternFlag = 0
        CanMsg[1].RemoteFlag = 0
        CanMsg[1].ID = 0x7D1
        CanMsg[1].DataLen = 8
        CanMsg[1].Data[0] = 0x22
        CanMsg[1].Data[1] = 0xAA
        CanMsg[1].Data[2] = 0xBB
        CanMsg[1].Data[3] = 0xCC
        CanMsg[1].Data[4] = 0xDD
        CanMsg[1].Data[5] = 0xEE
        CanMsg[1].Data[6] = 0xFF
        CanMsg[1].Data[7] = 0x00

        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 2)

        if SendedNum >= 0:
            pass
            #print("Write SK128_02 Success send frames:%d" % SendedNum)
    def ClearSK128_0(self):
        CanMsg = (CAN_MSG * 1)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x7D1
        CanMsg[0].DataLen = 8
        CanMsg[0].Data[0] = 0x10
        CanMsg[0].Data[1] = 0x13
        CanMsg[0].Data[2] = 0x2E
        CanMsg[0].Data[3] = 0x71
        CanMsg[0].Data[4] = 0x31
        CanMsg[0].Data[5] = 0x00
        CanMsg[0].Data[6] = 0x11
        CanMsg[0].Data[7] = 0x22

        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 1)
    def ClearSK128_1(self):
        CanMsg = (CAN_MSG * 2)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x7D1
        CanMsg[0].DataLen = 8
        CanMsg[0].Data[0] = 0x21
        CanMsg[0].Data[1] = 0x33
        CanMsg[0].Data[2] = 0x44
        CanMsg[0].Data[3] = 0x55
        CanMsg[0].Data[4] = 0x66
        CanMsg[0].Data[5] = 0x77
        CanMsg[0].Data[6] = 0x88
        CanMsg[0].Data[7] = 0x99
        CanMsg[1].ExternFlag = 0
        CanMsg[1].RemoteFlag = 0
        CanMsg[1].ID = 0x7D1
        CanMsg[1].DataLen = 8
        CanMsg[1].Data[0] = 0x22
        CanMsg[1].Data[1] = 0xAA
        CanMsg[1].Data[2] = 0xBB
        CanMsg[1].Data[3] = 0xCC
        CanMsg[1].Data[4] = 0xDD
        CanMsg[1].Data[5] = 0xEE
        CanMsg[1].Data[6] = 0xFF
        CanMsg[1].Data[7] = 0x00

        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 2)
    def ClearDTC(self):
        CanMsg = (CAN_MSG * 1)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x7D1
        CanMsg[0].DataLen = 8
        CanMsg[0].Data[0] = 0x04
        CanMsg[0].Data[1] = 0x14
        CanMsg[0].Data[2] = 0xFF
        CanMsg[0].Data[3] = 0xFF
        CanMsg[0].Data[4] = 0xFF
        CanMsg[0].Data[5] = 0x00
        CanMsg[0].Data[6] = 0x00
        CanMsg[0].Data[7] = 0x00
        CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 2)
    def ChangeLearningStatusToVirgin(self):
        CanMsg = (CAN_MSG * 1)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x7D1
        CanMsg[0].DataLen = 8
        CanMsg[0].Data[0] = 0x07
        CanMsg[0].Data[1] = 0x2E
        CanMsg[0].Data[2] = 0xFD
        CanMsg[0].Data[3] = 0x00
        CanMsg[0].Data[4] = 0x01
        CanMsg[0].Data[5] = 0x00
        CanMsg[0].Data[6] = 0x00
        CanMsg[0].Data[7] = 0x00
        CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 2)
    def Cal_AES128_compare(self, data):
        #check_count = 0
        temp = list(range(16))
        check_data = [0x00, 0x00, 0x00, 0x00, 0x00, 0x11, 0x22, 0x33, 0x94, 0x25, 0x45, 0x47, 0x46, 0x4A, 0x5B, 0x7D]
        aes128data = [0x94, 0x25, 0x45, 0x47, 0x46, 0x4A, 0x5B, 0x7D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        caldata    = list(range(8))
        for i in range(4):
            check_data[i] = data[i]
        key = prpcrypt(b'\x00\x11\x22\x33\x44\x55\x66\x77\x88\x99\xaa\xbb\xcc\xdd\xee\xff')  # init key

        aes = key.encrypt(bytes(check_data))     # ESCL
        _aes = (a2b_hex(aes))
        for i in range(16):
            temp[i] = _aes[i]

        if temp[0:4] == data[4:9]:
            for i in range(8):
                aes128data[i+8] = temp[i+8]
            aes = key.encrypt(bytes(aes128data)) # PEPS
            _aes = a2b_hex(aes)
            for i in range(8):
                caldata[i] = int(_aes[i+8])
            #print((caldata))
            #print("Caldata:", caldata)
            return caldata
    def Send_AES128_Data(self,data):
        CanMsg = (CAN_MSG * 1)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x104
        CanMsg[0].DataLen = 8
        for i in range(8):
            CanMsg[0].Data[i] = data[i]
        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 1)
    def EnterExtendedSession(self):
        CanMsg = (CAN_MSG * 1)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x7D1
        CanMsg[0].DataLen = 8
        CanMsg[0].Data[0] = 0x02
        CanMsg[0].Data[1] = 0x10
        CanMsg[0].Data[2] = 0x03
        for i in range(0, 5):
            CanMsg[0].Data[i + 3] = 0x00
        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 1)
    def SendInExtendedSession(self):
        CanMsg = (CAN_MSG * 1)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x7D1
        CanMsg[0].DataLen = 8
        CanMsg[0].Data[0] = 0x02
        CanMsg[0].Data[1] = 0x3E
        CanMsg[0].Data[2] = 0x00
        for i in range(0, 5):
            CanMsg[0].Data[i + 3] = 0x00
        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 1)
    def GetAccessSeed(self):
        CanMsg = (CAN_MSG * 1)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x7D1
        CanMsg[0].DataLen = 8
        CanMsg[0].Data[0] = 0x02
        CanMsg[0].Data[1] = 0x27
        CanMsg[0].Data[2] = 0x01
        for i in range(0, 5):
            CanMsg[0].Data[i + 3] = 0x00
        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 1)
    def EN_Access(self,data):
        #print(data)
        CanMsg = (CAN_MSG * 1)()
        CanMsg[0].ExternFlag = 0
        CanMsg[0].RemoteFlag = 0
        CanMsg[0].ID = 0x7D1
        CanMsg[0].DataLen = 8
        CanMsg[0].Data[0] = 0x06
        CanMsg[0].Data[1] = 0x27
        CanMsg[0].Data[2] = 0x02
        CanMsg[0].Data[7] = 0xAA
        for i in range(0, 4):
            CanMsg[0].Data[i + 3] = data[i]

        t = time.time()
        #for i in range(len(CanMsg[0].Data)):print(hex(CanMsg[0].Data[i]), end=" ")
       # print("")
        SendedNum = CAN_SendMsg(self.DevHandles[0], self.CANIndex, byref(CanMsg[0]), 1)
    def Cal_Key(self,list):
        #print("list:")
        #for i in range(len(list)):print(hex(list[i]), end=" ")
        #print("")
        seedArray = [0x00, 0x00, 0x00, 0x00]
        calData = [0, 0, 0, 0]
        returnKey = [0, 0, 0, 0]
        xorArray = [0xE9, 0x4A, 0x22, 0x91]
        if len(list) == 8:
            for i in range(4):
                seedArray[i] = list[i+3]
        #for i in range(len(seedArray)):print(hex(seedArray[i]), end=" ")
        #print("")
        for i in range(4):
            calData[i] = seedArray[i] ^ xorArray[i]
        returnKey[0] = ((calData[3] & 0x0F) << 4) | (calData[3] & 0xF0)
        returnKey[1] = ((calData[1] & 0x0F) << 4) | ((calData[0] & 0xF0) >> 4)
        returnKey[2] = (calData[1] & 0xF0) | (calData[2] & 0xF0) >> 4
        returnKey[3] = ((calData[0] & 0x0F) << 4) | (calData[2] & 0x0F)
        #for i in range(len(returnKey)):print(hex(returnKey[i]), end=" ")
        #print("")
        return returnKey
    def timer(self):
        self.timerMark ^= 1
        #if self.timerCount == 50000:
            #self.testTimer.stop()
    def time(self):
        self.testTimer = QTimer(self)
        self.testTimer.timeout.connect(self.timer)
        self.testTimer.start(5) #5ms

    def run(self):

        #GPIO_Write(self.DevHandles[0], 0xAA00, 1)
        if self.count_mark == 0:
            self.GetF180()
        if self.count_mark == 1:
            self.GetF18C()
        if self.count_mark == 2:
            self.GetF193()
        if self.count_mark == 3:
            self.GetF195()
        if self.count_mark == 4:
            self.GetF187()
        if self.count_mark == 5:
            self.GetF18A()
        if self.count_mark == 6:
            self.GetF18B()
        if self.count_mark == 7:
            self.EnterExtendedSession()
        if self.count_mark == 8:
            self.SendInExtendedSession()
        if self.count_mark == 9:
            self.GetAccessSeed()
        #if self.count_mark == 11:
            #self.WriteSK128_1()

        _timerMark = 1 if self.timerMark == 1 else 0
        if (_timerMark ^ self._timerMark) & _timerMark:
            self.count_Periodic += 1

            self.DiagReq_Enable += 1
            self.timerCount += 1
            # print(self.DiagReq_Enable, time.time())
        self._timerMark = _timerMark
        # self.Exec_AES128_compare([0xf3, 0xcd, 0x10, 0xdd, 0x8c, 0x22, 0xae, 0xfb])
        # print(self.product_info)
        if self.TestStatus == 0 or self.TestModel == 0:
            if self.count_mark > 10 and self.write_sk128_mark == 1:
                if self.DiagReq_Enable % 1 == 0 and self.last_count_0 != self.DiagReq_Enable:
                    self.last_count_0 = self.DiagReq_Enable
                    self.SendPeriodic_Msg_10ms()
                    # print('10ms', time.time(), self.DiagReq_Enable)
                if self.DiagReq_Enable % 2 == 0 and self.last_count_1 != self.DiagReq_Enable:
                    self.last_count_1 = self.DiagReq_Enable
                    self.SendPeriodic_Msg_20ms()
                    # print('20ms', time.time(), self.DiagReq_Enable)
                if self.DiagReq_Enable % 5 == 0 and self.last_count_2 != self.DiagReq_Enable:
                    self.last_count_2 = self.DiagReq_Enable
                    if self.mark_1 == 1:
                        self.Get7109()
                if self.DiagReq_Enable % 8 == 0 and self.last_count_3 != self.DiagReq_Enable:
                    self.last_count_3 = self.DiagReq_Enable
                    if self.mark == 1:
                        self.Get7107()
                if self.DiagReq_Enable % 10 == 0 and self.last_count_4 != self.DiagReq_Enable:
                    self.last_count_4 = self.DiagReq_Enable
                    self.SendPeriodic_Msg_100ms()
                    # print('100ms', time.time(), self.DiagReq_Enable)
            if self.DiagReq_Enable % 50 == 0 and self.last_count_5 != self.DiagReq_Enable:
                self.last_count_5 = self.DiagReq_Enable
                self.SendPeriodic_Msg()
            # print('500ms',time.time(), self.DiagReq_Enable)
        '''
        if self.DiagReq_Enable % 1000 == 0 and self.last_count_7 != self.DiagReq_Enable:
            self.last_count_7 = self.DiagReq_Enable
            gpio_data = 0x200 - self.last_gpio_WT_data
            print(gpio_data)
            GPIO_Write(self.DevHandles[0], 0x200, gpio_data)
            self.last_gpio_WT_data = gpio_data
        '''

        if self.count_mark == 0: GPIO_Write(self.DevHandles[0], 0x200, 0x200)
        if self.count_mark == 11: GPIO_Write(self.DevHandles[0], 0x200, 0x000)

        self.no_msg_count = 0
        # Product information
        CanMsgBuffer = (CAN_MSG * 10240)()
        CanNum = CAN_GetMsg(self.DevHandles[0], self.CANIndex, byref(CanMsgBuffer))
        if CanNum > 0:
            for i in range(0, CanNum):
                #self.count += 1

                print(("%04X " % CanMsgBuffer[i].ID), ' ', end='')

                for j in range(0, CanMsgBuffer[i].DataLen):
                    print("%02X " % CanMsgBuffer[i].Data[j], end='')
                print("", self.count_mark, self.mark, self.last_count_6)

                if CanMsgBuffer[i].ID == 0x7D9:
                    if CanMsgBuffer[i].Data[3] == 0xF1 and CanMsgBuffer[i].Data[4] == 0x80 and self.count_mark == 0:
                        self.product_info['F180'] = (chr(CanMsgBuffer[i].Data[5]) +
                                                     chr(CanMsgBuffer[i].Data[6]) +
                                                     chr(CanMsgBuffer[i].Data[7]))
                        # if self.DiagReq_Enable == 10:
                    if CanMsgBuffer[i].Data[0] == 0x21 and self.count_mark == 0:
                        for j in range(7):
                            self.product_info['F180'] += chr(CanMsgBuffer[i].Data[j + 1])
                    if CanMsgBuffer[i].Data[0] == 0x22 and self.count_mark == 0:
                        for K in range(6):
                            self.product_info['F180'] += chr(CanMsgBuffer[i].Data[K + 1])
                        self.countGet += 1
                        if self.countGet > 0:
                            self.countGet = 0
                            self.count_mark = 1
                            break

                    if CanMsgBuffer[i].Data[3] == 0xF1 and CanMsgBuffer[i].Data[4] == 0x8C and self.count_mark == 1:
                        self.product_info['F18C'] = (chr(CanMsgBuffer[i].Data[5]) +
                                                     chr(CanMsgBuffer[i].Data[6]) +
                                                     chr(CanMsgBuffer[i].Data[7]))
                        # if self.DiagReq_Enable == 10:
                    if CanMsgBuffer[i].Data[0] == 0x21 and self.count_mark == 1:
                        for j in range(7):
                            self.product_info['F18C'] += chr(CanMsgBuffer[i].Data[j + 1])
                    if CanMsgBuffer[i].Data[0] == 0x22 and self.count_mark == 1:
                        for K in range(6):
                            self.product_info['F18C'] += chr(CanMsgBuffer[i].Data[K + 1])
                        self.countGet += 1
                        if self.countGet > 1:
                            self.countGet = 0
                            self.count_mark = 2
                            break

                    if CanMsgBuffer[i].Data[3] == 0xF1 and CanMsgBuffer[i].Data[4] == 0x93 and self.count_mark == 2:
                        self.product_info['F193'] = (chr(CanMsgBuffer[i].Data[5]) +
                                                     chr(CanMsgBuffer[i].Data[6]) +
                                                     chr(CanMsgBuffer[i].Data[7]))
                        # if self.DiagReq_Enable == 10:
                    if CanMsgBuffer[i].Data[0] == 0x21 and self.count_mark == 2:
                        for j in range(7):
                            self.product_info['F193'] += chr(CanMsgBuffer[i].Data[j + 1])
                    if CanMsgBuffer[i].Data[0] == 0x22 and self.count_mark == 2:
                        for K in range(6):
                            self.product_info['F193'] += chr(CanMsgBuffer[i].Data[K + 1])
                        self.countGet += 1
                        if self.countGet > 1:
                            self.countGet = 0
                            self.count_mark = 3
                            break

                    if CanMsgBuffer[i].Data[3] == 0xF1 and CanMsgBuffer[i].Data[4] == 0x95 and self.count_mark == 3:
                        self.product_info['F195'] = (chr(CanMsgBuffer[i].Data[5]) +
                                                     chr(CanMsgBuffer[i].Data[6]) +
                                                     chr(CanMsgBuffer[i].Data[7]))
                        # if self.DiagReq_Enable == 10:
                    if CanMsgBuffer[i].Data[0] == 0x21 and self.count_mark == 3:
                        for j in range(7):
                            self.product_info['F195'] += chr(CanMsgBuffer[i].Data[j + 1])
                    if CanMsgBuffer[i].Data[0] == 0x22 and self.count_mark == 3:
                        for K in range(6):
                            self.product_info['F195'] += chr(CanMsgBuffer[i].Data[K + 1])
                        self.countGet += 1
                        if self.countGet > 1:
                            self.countGet = 0
                            self.count_mark = 4
                            break
                    if CanMsgBuffer[i].Data[3] == 0xF1 and CanMsgBuffer[i].Data[4] == 0x87 and self.count_mark == 4:
                        self.product_info['F187'] = (chr(CanMsgBuffer[i].Data[5]) +
                                                     chr(CanMsgBuffer[i].Data[6]) +
                                                     chr(CanMsgBuffer[i].Data[7]))
                        # if self.DiagReq_Enable == 10:
                    if CanMsgBuffer[i].Data[0] == 0x21 and self.count_mark == 4:
                        for j in range(7):
                            self.product_info['F187'] += chr(CanMsgBuffer[i].Data[j + 1])
                        self.countGet += 1
                        if self.countGet > 1:
                            self.countGet = 0
                            self.count_mark = 5
                            break
                    if CanMsgBuffer[i].Data[3] == 0xF1 and CanMsgBuffer[i].Data[4] == 0x8A and self.count_mark == 5:
                        self.product_info['F18A'] = ''
                        self.product_info['F18A'] = (chr(CanMsgBuffer[i].Data[5]) +
                                                     chr(CanMsgBuffer[i].Data[6]) +
                                                     chr(CanMsgBuffer[i].Data[7]))
                        # if self.DiagReq_Enable == 10:
                    if CanMsgBuffer[i].Data[0] == 0x21 and CanMsgBuffer[i].Data[4] == 0xAA and self.count_mark == 5:
                        for j in range(3):
                            self.product_info['F18A'] += chr(CanMsgBuffer[i].Data[j + 1])

                        self.countGet += 1
                        print("in count 5", self.countGet)
                        if self.countGet > 1:
                            self.countGet = 0
                            self.count_mark = 6
                            break
                    if CanMsgBuffer[i].Data[2] == 0xF1 and CanMsgBuffer[i].Data[3] == 0x8B and self.count_mark == 6:
                        self.product_info['F18B'] = (self.chr_load(CanMsgBuffer[i].Data[4]) +
                                                     self.chr_load(CanMsgBuffer[i].Data[5]) +
                                                     self.chr_load(CanMsgBuffer[i].Data[6]) +
                                                     self.chr_load(CanMsgBuffer[i].Data[7]))
                        print(self.product_info['F18B'])
                        self.countGet += 1
                        if self.countGet > 1:
                            self.countGet = 0
                            self.count_mark = 7
                            break
                    if CanMsgBuffer[i].Data[0] == 0x06 and CanMsgBuffer[i].Data[1] == 0x50 \
                            and CanMsgBuffer[i].Data[2] == 0x03 and self.count_mark == 7:
                        self.countGet += 1
                        if self.countGet > 1:
                            self.countGet = 0
                            self.count_mark = 8
                            break
                    if CanMsgBuffer[i].Data[0] == 0x02 and CanMsgBuffer[i].Data[1] == 0x7E \
                            and CanMsgBuffer[i].Data[2] == 0x00 and self.count_mark == 8:
                        self.countGet += 1
                        if self.countGet > 1:
                            self.countGet = 0
                            self.count_mark = 9
                        break
                    # 9
                    if CanMsgBuffer[i].Data[0] == 0x06 and CanMsgBuffer[i].Data[1] == 0x67 \
                            and CanMsgBuffer[i].Data[2] == 0x01:
                        self.EN_Access(self.Cal_Key(CanMsgBuffer[i].Data))
                        self.count_mark = 10
                        #print(self.count, ("%04X " % CanMsgBuffer[i].ID), ' ', end='')
                        for j in range(0, CanMsgBuffer[i].DataLen):
                            pass
                            #print("%02X " % CanMsgBuffer[i].Data[j], end='')
                        print("")
                        break
                    # 10
                    if (CanMsgBuffer[i].Data[0] == 0x02 and CanMsgBuffer[i].Data[1] == 0x67 and\
                            CanMsgBuffer[i].Data[2] == 0x02) or self.count_mark == 10:
                        self.sleep(0.05)
                        if self.clear_DTC_mark == 0:
                            self.WriteSK128_0()
                            print("write0")
                        elif self.clear_DTC_mark == 1:
                            self.ClearSK128_0()
                            print("Clear0")
                        self.count_mark = 11
                        break
                    # 11
                    if (CanMsgBuffer[i].Data[0] == 0x30 and CanMsgBuffer[i].Data[1] == 0x00 and\
                            CanMsgBuffer[i].Data[2] == 0x0A):
                        self.sleep(0.05)
                        if self.clear_DTC_mark == 0:
                            self.WriteSK128_1()
                            print("write1")

                        elif self.clear_DTC_mark == 1:
                            self.ClearSK128_1()
                            print("Clear1")
                        break
                    if (CanMsgBuffer[i].Data[0] == 0x03 and CanMsgBuffer[i].Data[1] == 0x6E\
                            and CanMsgBuffer[i].Data[2] == 0x71):
                        self.write_sk128_mark = 1
                        self.count_mark = 12
                        self.clear_DTC_mark = 0
                        self.ChangeLearningStatusToVirgin()
                        print(self.count_mark, "-----------------------write1 SUSSCE---------------------------")
                        break
                    # 7109
                    if CanMsgBuffer[i].Data[2] == 0x71 and CanMsgBuffer[i].Data[3] == 0x09:
                        self.product_info['7109'] = (self.chr_load(CanMsgBuffer[i].Data[4]))
                        self.mark_1 = 0
                    # 7107
                    if CanMsgBuffer[i].Data[2] == 0x71 and CanMsgBuffer[i].Data[3] == 0x07:
                        self.product_info['7107'] = (self.chr_load(CanMsgBuffer[i].Data[4]))
                        self.mark = 0



                if CanMsgBuffer[i].ID == 0x105:

                    temp = self.Cal_AES128_compare(CanMsgBuffer[i].Data)
                    _temp = list(range(8))
                    for i in range(8):_temp[i] = int(temp[i])
                    #print(temp)
                    self.Send_AES128_Data(_temp)
                    #print("temp:", _temp, CanMsgBuffer[i].ID, CanMsgBuffer[i].Data[0])

                    self.count_mark = 26

                    break
                
                if CanMsgBuffer[i].ID == 0x279:

                    if self.count_mark == 25:
                        if CanMsgBuffer[i].Data[0] == 0x20:
                            # self.count += 1
                            '''
                            GPIO_Write(self.DevHandles[0], 0x200, 0x200)
                            self.msleep(300)
                            GPIO_Write(self.DevHandles[0], 0x200, 0x000)
                            '''
                            self.Lock()
                            print('lock')
                            self.count_mark = 26

                            # print("lock!")
                        elif CanMsgBuffer[i].Data[0] == 0x21:
                            self.UnLock()
                            print('Unlock')
                    if CanMsgBuffer[i].Data[0] != self.last_status:
                        self.last_status = CanMsgBuffer[i].Data[0]
                        self.mark = 1
                        self.mark_1 = 1
                    self._response = ''
                    for j in range(0, CanMsgBuffer[i].DataLen):
                        self._response += ("%02X  " % CanMsgBuffer[i].Data[j])

        self.dataSignal.emit(self.product_info, self._response)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ui = MainUI()
    ui.show()
    sys.exit(app.exec_())
