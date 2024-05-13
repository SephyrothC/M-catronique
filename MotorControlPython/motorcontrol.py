#============================================================
# Motor control libray
#     Author: F. CRISON
#     Version: 1.0.0
#============================================================
from ctypes.wintypes import BYTE, CHAR
from serial.serialutil import Timeout
import serial.tools.list_ports
import serial
import struct
from enum import Enum
import array
import numpy
import time

# Procotol byte order: little-endian
#                      ==========
#Numbers in "pseudo hexa" ASCII format   e.g: 0=0x30  1=0x31  ... E=0x3E F=0x3F ...)

#============================================================
#Data frame structure
# [  1 byte   ]   [  1 byte  ]  [  1 byte  ]  [ 0 to N byte ]  [ 1 byte  ] 
# [FRAME_START]   [frame code]  [frame_type]  [....data.....]  [FRAME_END] 
# 
#  [frame code] : code of the frame : 'A', 'B', ...;
# 
# frame_type  : 
#     'e' (0x65) = empty (no data -> command frame)
#     'b' (0x62) = integer 8 bits
#     's' (0x73) = integer 16 bits
#     'i' (0x6C) = integer 32 bits
#     'f' (0x66) = float 32 bits
#     
# DATA: Numbers in "pseudo hexa" ASCII format   e.g: 0=0x30  1=0x31  ... E=0x3E F=0x3F ...
# number=0x3AB9  ==>  data= [0x33 0x3A 0x3B 0x39]
FRAME_START=0x55
FRAME_STOP=0xAA
#============================================================

testProtocol=0 # only for test

def findSerialPort(manufacturer:str):
    """Find serial port of connected STM32 board
        Parameters:
    manufaturer (string): usb serial manufacturer
        Returns:
    String: serial port name or empty string if not found 
    """
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if (p.manufacturer=="STMicroelectronics"):
            return p.device
    return ""


def openSerialSTM32():
    """Open serial communication with STM32 board
    """
    comPort=findSerialPort("STMicroelectronics")
    if (comPort==""):
        print("!!! Board not found or not connected !!!")
        exit()
    # Open serial port   (read timeout=100ms)
    serialPort=serial.Serial(port=comPort,baudrate=115200,timeout=0.1)
    return serialPort

def writeSerial(p_serial:serial, p_char:int):
    p_serial.write(bytes([p_char]))

def writeByte(p_serial:serial, p_byte:int):
    """Write a 8 bits integer in "pseudo hexa" ascii format on serial port
    """
    p_serial.write(bytes([0x30|(numpy.right_shift(numpy.uint32(p_byte),4)&0x0F)]))
    p_serial.write(bytes([0x30|(p_byte&0x0F)]))


def writeShort(p_serial:serial, p_short:int):
    """Write a 16 bits integer in "pseudo hexa" ascii format- little-endian on serial port
    """
    conv=struct.pack('<h',p_short) #short to bytes
    writeByte(p_serial,conv[0])
    writeByte(p_serial,conv[1])


def writeInt(p_serial:serial, p_int:int):
    """Write a 32 bits integer in "pseudo hexa" ascii format- little-endian on serial port
    """
    conv=struct.pack('<i',p_int) #int to bytes
    writeByte(p_serial,conv[0])
    writeByte(p_serial,conv[1])
    writeByte(p_serial,conv[2])
    writeByte(p_serial,conv[3])


def writeFloat(p_serial:serial, p_float:float):
    """Write a 32 bits float in "pseudo hexa" ascii format- little-endian on serial port
    """
    conv=struct.pack('<f',p_float) #float to bytes
    writeByte(p_serial,conv[0])
    writeByte(p_serial,conv[1])
    writeByte(p_serial,conv[2])
    writeByte(p_serial,conv[3])


def writeFrameStart(p_serial:serial):
    """Write start frame byte on serial port
    """
    p_serial.write(bytes([FRAME_START]))  


def writeFrameStop(p_serial:serial):
    """Write stop frame byte on serial port
    """
    p_serial.write(bytes([FRAME_STOP]))  


def writeFrame(p_serial:serial,p_code:int):
    """Write a frame without any data
    """
    if (type(p_code) is str):
       p_code=ord(p_code)   
    writeFrameStart(p_serial)
    writeSerial(p_serial,p_code)
    writeSerial(p_serial,ord('e'))
    writeFrameStop(p_serial)


def writeFrameByte(p_serial:serial,p_code,p_bytes:array):
    """Write a frame with x bytes
    """
    if (type(p_code) is str):
        p_code=ord(p_code)
    writeFrameStart(p_serial)
    writeSerial(p_serial,p_code)
    writeSerial(p_serial,ord('b'))
    for i in range(0, len(p_bytes)):
        writeByte(p_serial,p_bytes[i])
    writeFrameStop(p_serial)

def writeFrameShort(p_serial:serial,p_code,p_short:array):
    """Write a frame with x shorts
    """
    if (type(p_code) is str):
        p_code=ord(p_code)
    writeFrameStart(p_serial)
    writeSerial(p_serial,p_code)
    writeSerial(p_serial,ord('s'))
    for i in range(0, len(p_short)):
        writeShort(p_serial,p_short[i])
    writeFrameStop(p_serial)


def writeFrameInt(p_serial:serial,p_code,p_int:array):
    """Write a frame with x ints
    """
    if (type(p_code) is str):
        p_code=ord(p_code)  
    writeFrameStart(p_serial)
    writeSerial(p_serial,p_code)
    writeSerial(p_serial,ord('i'))
    for i in range(0, len(p_int)):
        writeInt(p_serial,p_int[i])
    writeFrameStop(p_serial)


def writeFrameFloat(p_serial:serial,p_code,p_float:array):
    """Write a frame with x floats
    """
    if (type(p_code) is str):
        p_code=ord(p_code)
    writeFrameStart(p_serial)
    writeSerial(p_serial,p_code)
    writeSerial(p_serial,ord('f'))
    for i in range(0, len(p_float)):
        writeFloat(p_serial,p_float[i])
    writeFrameStop(p_serial)


class RxState(Enum):
    IDLE = 0
    R_FRAME_START = 1
    R_FRAME_CODE = 2
    R_FRAME_TYPE = 3
    R_FRAME_STOP = 4


def onNewFrameCommandDefault(l_frameCode:int):
    print(f"onNewFrameCommand undefined (code='{chr(l_frameCode)}')")
def onNewFrameByteDefault(p_frameCode:int,p_byte:array):
    print(f"onNewFrameByte undefined (code='{chr(l_frameCode)}')")
    print(p_byte)
def onNewFrameShortDefault(p_frameCode:int,p_short:array):
    print(f"onNewFrameShort undefined (code='{chr(l_frameCode)}')")
    print(p_short)
def onNewFrameIntDefault(p_frameCode:int,p_int:array):
    print(f"onNewFrameInt undefined (code='{chr(l_frameCode)}')")
    print(p_int)
def onNewFrameFloatDefault(p_frameCode:int,p_float:array):
    print(f"onNewFrameFloat undefined (code='{chr(l_frameCode)}')")
    print(p_float)

l_stateRx=RxState.IDLE #wait for FRAME_START
l_frameCode=0
l_frameType=0
l_conv=array.array('b')
l_receiveCount=0
l_data=array.array('h')
l_pseudoHexa=array.array('B',[0,0])
l_pseudoHexaCnt=0


onNewFrameCommandCallback=onNewFrameCommandDefault
onNewFrameByteCallback=onNewFrameByteDefault
onNewFrameShortCallback=onNewFrameShortDefault
onNewFrameIntCallback=onNewFrameIntDefault
onNewFrameFloatCallback=onNewFrameFloatDefault

def onReceiveCar(p_car:int):
    """Protocol management
    """
    global l_stateRx
    global l_frameCode
    global l_frameType
    global  l_receiveCount
    global l_data
    global l_conv
    global l_pseudoHexa
    global l_pseudoHexaCnt
    global testProtocol

    if(p_car == FRAME_STOP):
        l_stateRx=RxState.R_FRAME_STOP

    # switch "state"
    if l_stateRx == RxState.R_FRAME_STOP: #end of frame
        # 'e' (0x65) = command frame
        if l_frameType == ord('e'):
            if testProtocol == 1:
                onNewFrameTest(l_frameCode,0)
            else :
                onNewFrameCommandCallback(l_frameCode)
        # 'b' (0x62) = integer 8 bits
        elif l_frameType == ord('b'):
            if testProtocol == 1:
                onNewFrameTest(l_frameCode,l_data)
            else :
                onNewFrameByteCallback(l_frameCode,l_data)
         # 's' (0x73) = integer 16 bits
        elif l_frameType == ord('s'):
            if testProtocol == 1:
                onNewFrameTest(l_frameCode,l_data)
            else :
                onNewFrameShortCallback(l_frameCode,l_data)
         # 'i' (0x6C) = integer 32 bits
        elif l_frameType == ord('i'):
            if testProtocol == 1:
                onNewFrameTest(l_frameCode,l_data)
            else :
                onNewFrameIntCallback(l_frameCode,l_data)
         # 'f' (0x66) = float 32 bits
        elif l_frameType == ord('f'):
            if testProtocol == 1:
                onNewFrameTest(l_frameCode,l_data)
            else :
                onNewFrameFloatCallback(l_frameCode,l_data)
        l_receiveCount=0
        l_dataCount=0
        l_conv=array.array('b')
        l_data=array.array('h')
        l_pseudoHexaCnt=0
        l_stateRx=RxState.IDLE
    elif l_stateRx == RxState.IDLE:
        if p_car == FRAME_START:
            l_stateRx=RxState.R_FRAME_START
    elif l_stateRx == RxState.R_FRAME_START:  #receive frame code
        l_frameCode=p_car
        l_stateRx=RxState.R_FRAME_CODE  
    elif l_stateRx == RxState.R_FRAME_CODE:
        l_frameType=p_car
        l_stateRx=RxState.R_FRAME_TYPE
        if l_frameType == ord('b'):
            l_data=array.array('b') # signed char
        elif l_frameType == ord('s'):
             l_data=array.array('h') # signed short           
        elif l_frameType == ord('i'):
             l_data=array.array('i') # signed int         
        elif l_frameType == ord('f'):
             l_data=array.array('f') # float   
    elif l_stateRx == RxState.R_FRAME_TYPE:
        if l_pseudoHexaCnt == 0:
            l_pseudoHexaCnt=1
            l_pseudoHexa[0]=p_car
            return
        else:
            l_pseudoHexa[1]=p_car
            l_pseudoHexaCnt=0
	        #pseudo hexa to char conv
            p_car=((l_pseudoHexa[0]&0x0F)<<4) | (l_pseudoHexa[1]&0x0F)
            if (p_car>127):
                p_car= (256-p_car) * (-1)        
        l_conv.append(p_car)
        l_receiveCount+=1
        # 'b' (0x62) = integer 8 bits
        if l_frameType == ord('b'):
            l_data.append(p_car)
            l_conv=array.array('b')
            l_receiveCount=0
        # 's' (0x73) = integer 16 bits
        elif l_frameType == ord('s'):
            if l_receiveCount == 2 :
                l_data.append(struct.unpack('<h',l_conv)[0])
                l_conv=array.array('b')
                l_receiveCount=0
        # 'i' (0x6C) = integer 32 bits
        elif l_frameType == ord('i'):
            if l_receiveCount == 4 :
                l_data.append(struct.unpack('<i',l_conv)[0])
                l_conv=array.array('b')
                l_receiveCount=0
        # 'f' (0x66) = float 32 bits
        elif l_frameType == ord('f'):
            if l_receiveCount == 4 :
                l_data.append(struct.unpack('<f',l_conv)[0])
                l_conv=array.array('b')
                l_receiveCount=0
    else:
        # default
        pass

def protocol(p_serial:serial):
    while p_serial.in_waiting:
        onReceiveCar(ord(p_serial.read(1)))


####################################################################################################
## for test only
####################################################################################################
testData=0
testFrameCode=0
libraryTestError=0

def onNewFrameTest(p_frameCode,p_data):
    global testData
    global testFrameCode
    testFrameCode=p_frameCode
    testData=p_data

def validateTest(p_frameCode,p_data):
    global testData
    global testFrameCode
    global libraryTestError
    if testFrameCode != ord(p_frameCode) or numpy.array_equal(p_data,testData)==False: 
        libraryTestError+=1
        print("")
        print(f"Error seq:{p_frameCode}({hex(ord(p_frameCode))})==>{chr(testFrameCode)}({hex(testFrameCode)})")
        print(f"Send data   :{p_data}")
        print(f"Receive data:{testData}")
        print("")

def protocolLibraryTest(p_serial:serial):
    global testProtocol
    global libraryTestError    
    
    testProtocol=1 
        #Mode test timeout
    waitTestTime=0.05

    print("==== Protocol library test : begin ====")
    libraryTestError=0

    writeFrame(p_serial,254)
    timeoutEnd=time.time()+waitTestTime
    while time.time()<timeoutEnd:
        protocol(p_serial)

    writeFrame(p_serial,'A')
    timeoutEnd=time.time()+waitTestTime
    while time.time()<timeoutEnd:
        protocol(p_serial)
    validateTest('A',0)

    l_val=numpy.linspace(-127,127,64)
    l_val=l_val.astype(numpy.byte)
    writeFrameByte(p_serial,'B',l_val)
    timeoutEnd=time.time()+waitTestTime
    while time.time()<timeoutEnd:
        protocol(p_serial)
    validateTest('B',l_val)

    l_val=numpy.linspace(-32768,32767,32)
    l_val=l_val.astype(numpy.short)
    writeFrameShort(p_serial,'C',l_val)
    timeoutEnd=time.time()+waitTestTime
    while time.time()<timeoutEnd:
        protocol(p_serial)
    validateTest('C',l_val)

    l_val=array.array('i',[0,1,2,3,1000,2000,1234567,-1234567])
    l_val=numpy.linspace(-2147483648,2147483647,16)
    l_val=l_val.astype(numpy.int)
    writeFrameInt(p_serial,'D',l_val)
    timeoutEnd=time.time()+waitTestTime
    while time.time()<timeoutEnd:
        protocol(p_serial)
    validateTest('D',l_val)

    l_val=array.array('f',[0.0,1.0,2.0,-3.0,1000.1,2000.2,12345.67,-12345.67])
    writeFrameFloat(p_serial,'E',l_val)
    timeoutEnd=time.time()+waitTestTime
    while time.time()<timeoutEnd:
        protocol(p_serial)
    validateTest('E',l_val)

    #Mode test end
    writeFrame(p_serial,255)
    timeoutEnd=time.time()+0.1
    while time.time()<timeoutEnd:
        protocol(p_serial)  

    testProtocol=0 
    print(f"==== Protocol library test : end --> {libraryTestError} error(s)====")
