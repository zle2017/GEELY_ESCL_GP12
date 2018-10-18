# -*- coding: utf-8 -*-
"""
文件说明：USB2XXX LIN操作相关函数集合
更多帮助：www.usbxyz.com
"""
from ctypes import *
import platform
from usb_device import *

# 定义函数返回错误代码
LIN_SUCCESS            = (0)   # 函数执行成功
LIN_ERR_NOT_SUPPORT    = (-1)  # 适配器不支持该函数
LIN_ERR_USB_WRITE_FAIL = (-2)  # USB写数据失败
LIN_ERR_USB_READ_FAIL  = (-3)  # USB读数据失败
LIN_ERR_CMD_FAIL       = (-4)  # 命令执行失败
LIN_ERR_CH_NO_INIT     = (-5)  # 该通道未初始化
LIN_ERR_READ_DATA      = (-6)  # LIN读数据失败
# LIN和校验模式
LIN_CHECK_MODE_STD    = 0
LIN_CHECK_MODE_EXT    = 1
LIN_NO_CHECK = 2
# BREAK位数定义
LIN_BREAK_BITS_10   = 0x00
LIN_BREAK_BITS_11   = 0x20
# 定义主从模式
LIN_MASTER         = 1
LIN_SLAVE          = 0
# 定义从机操作模式
LIN_SLAVE_WRITE    = 0
LIN_SLAVE_READ     = 1

# 定义初始化LIN初始化数据类型
class LIN_CONFIG(Structure):
    _fields_ = [
        ("BaudRate",c_uint),       # 波特率,最大20K
        ("CheckMode",c_ubyte),     # 校验模式，0-标准校验模式，1-增强校验模式（包含PID）
        ("MasterMode",c_ubyte),    # 主从模式，0-从模式，1-主模式
        ("BreakBits",c_ubyte),     # Break长度，0x00-10bit,0x20-11bit
    ]
# 设置从模式下ID操作模式
class SLAVE_LIN_DATA(Structure):
    _fields_ = [
        ("DataLen",c_ubyte),   # 从模式下发送数据的长度或者从模式接收数据的长度，不含校验字节
        ("WorkMode",c_ubyte),  # 0-从模式发送数据，1-从模式接收数据
        ("Data",c_ubyte*9),    # 从模式下接收到的数据字节或者待发送的数据字节
    ]
def LIN_Init(DevHandle,Channel,pConfig):
    return USB2XXXLib.LIN_Init(DevHandle,Channel,pConfig)

def LIN_WriteData(DevHandle,Channel,ID,pWriteData,WriteLen):
    return USB2XXXLib.LIN_WriteData(DevHandle,Channel,ID,pWriteData,WriteLen)

def LIN_ReadData(DevHandle,Channel,ID,pReadData):
    return USB2XXXLib.LIN_ReadData(DevHandle,Channel,ID,pReadData)

def LIN_SlaveSetIDOperation(DevHandle,Channel,ID,SlaveOperationData):
    return USB2XXXLib.LIN_SlaveSetIDOperation(DevHandle,Channel,ID,SlaveOperationData)

def LIN_SlaveGetData(DevHandle, Channel, pSlaveData):
    return USB2XXXLib.LIN_SlaveGetData(DevHandle, Channel, pSlaveData)

def LIN_BusConfig(DevHandle, DevIndex=0, LINCH=0, LINVer='2.1', Speed=0, Master=True):
    LINConfig = LIN_CONFIG()
    if LINVer == '2.0':
        LINConfig.CheckMode = LIN_CHECK_MODE_EXT
    elif LINVer =='1.0':
        LINConfig.CheckMode = LIN_CHECK_MODE_STD
    else:
        LINConfig.CheckMode = LIN_CHECK_MODE_EXT
    LINConfig.BaudRate = Speed
    if Master is True:
        LINConfig.MasterMode = 1
    if Master is False :
        LINConfig.MasterMode = 0
    return LIN_Init(DevHandle[DevIndex], LINCH, byref(LINConfig))

def LIN_SendMsg(DevHandle,DevIndex=0,LINCH=0,ID=hex,Data=list,Len=8):
    write_buffer = (c_byte*len(Data))()
    for i in range(len(Data)):
        write_buffer[i] = Data[i]
    return USB2XXXLib.LIN_WriteData(DevHandle[DevIndex], LINCH, ID, write_buffer, Len)

def LIN_Read(DevHandle,DevIndex=0,LINCH=0,ID=hex,Data=(c_ubyte*10)()):
    return USB2XXXLib.LIN_ReadData(DevHandle[DevIndex], LINCH, ID, Data)

def LIN_GetMsg(DevHandle,DevIndex=0,LINCH=0,ID=hex,Len=8,ValueType='Str'):
    Data = (c_ubyte * Len)()
    _Data = [0]*(Len+1)
    _Data[0] = hex(ID)
    ret = USB2XXXLib.LIN_ReadData(DevHandle[DevIndex], LINCH, ID, Data)
    if ret>LIN_SUCCESS:
        for i in range(0, ret):
            if ValueType == 'Str':
                _Data[i+1] = "0x%02X " %(Data[i])
            if ValueType == 'Hex':
                _Data[i+1] = hex(Data[i])
    if ValueType == 'Str':
        return _Data
    if ValueType == 'Hex':
        return _Data