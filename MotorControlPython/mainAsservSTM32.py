#============================================================
# Motor control loop in STM32 embedded board 
#     Author: F. CRISON
#     Version: 1.0.0
#============================================================
import motorcontrol
import array
import sys
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import threading

#============================================================
REF_VALUE_MIN=2048-1000
REF_VALUE_MAX=2048+1000
#============================================================

def getGraphTitleString():
    return ('Press a,b,-,+ P='+str(g_pidP))
def updateGraph():
    try:
        ax.cla()
        ax.set_title(getGraphTitleString())
        ax.plot(np.linspace(0,len(g_data1)*.01,len(g_data1)),g_data1)
        #Y autolimit (default: 0---4096)
        yMin=min(g_data1,default=0)
        yMin=min(0,yMin)
        yMax=max(g_data1,default=0)
        yMax=max(4096,yMax)
        ax.set_ylim([yMin,yMax])
        ax.grid(True)
        fig.canvas.draw()
    except NameError as e:
        pass
    
def graphMain():
    global fig
    global ax
    # Create a figure with only one subplot
    fig, ax = plt.subplots()
    fig.canvas.mpl_disconnect(fig.canvas.manager.key_press_handler_id)
    fig.canvas.mpl_connect('key_press_event', on_key)
    ax.set_title(getGraphTitleString())
    ax.grid(True)
    plt.show()


def onNewFrameCommand(l_frameCode:int):
    #TODO manage received data
    pass

def onNewFrameByte(p_frameCode:int,p_byte:array):
    #TODO manage received data
    pass

def onNewFrameShort(p_frameCode:int,p_short:array):
    #TODO manage received data
    global g_pidP
    global g_data1
    g_data1=p_short
    updateGraph()
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
    global g_pidP
    #print('press', event.key)
    sys.stdout.flush()
    if event.key == 'a':
        motorcontrol.writeFrameShort(stm32Serial,'A',[REF_VALUE_MAX])
    elif event.key == 'b':
        motorcontrol.writeFrameShort(stm32Serial,'A',[REF_VALUE_MIN])
    elif event.key == '+':
        g_pidP=g_pidP+1
        motorcontrol.writeFrameShort(stm32Serial,'P',[g_pidP])
    elif event.key == '-':
        if g_pidP>=2:
            g_pidP=g_pidP-1
        motorcontrol.writeFrameShort(stm32Serial,'P',[g_pidP])
    updateGraph()



######################################
#                                    #
#              MAIN                  #
#                                    #
######################################

#define callback data functions
motorcontrol.onNewFrameCommandCallback=onNewFrameCommand
motorcontrol.onNewFrameByteCallback=onNewFrameByte
motorcontrol.onNewFrameShortCallback=onNewFrameShort
motorcontrol.onNewFrameIntCallback=onNewFrameInt
motorcontrol.onNewFrameFloatCallback=onNewFrameFloat

#Library test
#stm32Serial=motorcontrol.openSerialSTM32()
#motorcontrol.protocolLibraryTest(stm32Serial)
#stm32Serial.close()

#Open serial port
stm32Serial=motorcontrol.openSerialSTM32()
#start communication thread
stop_threads = False
t1 = threading.Thread( target=protocolThread,args =(lambda : stop_threads,))
t1.start()
#Data graph
g_data1=array.array('h') #h=int16
#pid 'P' parameter
g_pidP=1
# Display main figure
graphMain()
#Stop thread and wait for end
stop_threads=True
t1.join()
#Close serial port
stm32Serial.close()

