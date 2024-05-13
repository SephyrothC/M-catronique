#============================================================
# Motor control template
#     Author: F. CRISON
#     Version: 1.0.0
#============================================================
import motorcontrol
import array
import sys
import numpy as np
import matplotlib.pyplot as plt
import threading
import csv

def onNewFrameCommand(l_frameCode:int):
    #TODO manage received data
    pass

def onNewFrameByte(p_frameCode:int,p_byte:array):
    #TODO manage received data
    pass

def onNewFrameShort(p_frameCode:int,p_short:array):
    #TODO manage received data
    global pid_p
    ax.cla()
    ax.set_title('Press a,b,-,+ P='+str(pid_p))
    ax.plot(np.linspace(0,len(p_short)*.01,len(p_short)),p_short)
    ax.set_ylim([0,4096])
    ax.grid(True)
    fig.canvas.draw()
    pass

def onNewFrameInt(p_frameCode:int,p_int:array):
     #TODO manage received data
    pass

def onNewFrameFloat(p_frameCode:int,p_float:array):
    #TODO manage received data
    pass


def protocolThread(stop):
    while stop() == False:
        motorcontrol.protocol(stm32Serial)  
    print("end")


def on_key(event):
    global pid_p
    print('press', event.key)
    sys.stdout.flush()
    if event.key == 'a':
        motorcontrol.writeFrameShort(stm32Serial,'A',[2048+1000])
    elif event.key == 'b':
        motorcontrol.writeFrameShort(stm32Serial,'A',[2048-1000])
    elif event.key == '+':
        pid_p=pid_p+1
        motorcontrol.writeFrameShort(stm32Serial,'P',[pid_p])
    elif event.key == '-':
        pid_p=pid_p-1
        motorcontrol.writeFrameShort(stm32Serial,'P',[pid_p])
    ax.set_title('Press a,b,-,+ P='+str(pid_p))
    fig.canvas.draw()    



motorcontrol.onNewFrameCommandCallback=onNewFrameCommand
motorcontrol.onNewFrameByteCallback=onNewFrameByte
motorcontrol.onNewFrameShortCallback=onNewFrameShort
motorcontrol.onNewFrameIntCallback=onNewFrameInt
motorcontrol.onNewFrameFloatCallback=onNewFrameFloat


stm32Serial=motorcontrol.openSerialSTM32()
motorcontrol.protocolLibraryTest(stm32Serial)
stm32Serial.close()


#Open serial port
stm32Serial=motorcontrol.openSerialSTM32()

pid_p=1

stop_threads = False
t1 = threading.Thread( target=protocolThread,args =(lambda : stop_threads,))
t1.start()

fig, ax = plt.subplots()
fig.canvas.mpl_connect('key_press_event', on_key)
ax.set_title('Press a,b,-,+ P='+str(pid_p))
ax.grid(True)
plt.show()

stop_threads=True
t1.join()

#To test the library
#stm32Serial=motorcontrol.openSerialSTM32()
#motorcontrol.protocolLibraryTest(stm32Serial)
#stm32Serial.close()


  
stm32Serial.close()

