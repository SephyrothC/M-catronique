#============================================================
# Motor control loop in Python
#     Author: F. CRISON
#     Version: 1.0.0
#============================================================
from time import sleep
import motorcontrol
import array
import sys
import numpy as np
import matplotlib.pyplot as plt
import threading

#============================================================
REF_VALUE_MIN=2048-1000
REF_VALUE_MAX=2048+1000
#============================================================



#============================================================
#            PID controller
#============================================================
def controlLoop(p_refValueIn,p_motorOut):
    #TODO PID calculation algorithm
    l_epsilon=(p_refValueIn-p_motorOut)
    l_outPid=l_epsilon*g_pidP* 0.610
    return l_outPid
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
    global g_refValueIn
    l_motorOut=int(p_short[0])
    if p_frameCode == ord('A'):
        if len(g_data1)<200:
            g_data1.append(l_motorOut)
        elif len(g_data1)  == 200 :
            g_data1.append(l_motorOut)
            updateGraph()
        ##### CONTROL LOOP #####     
        g_motorIn= controlLoop(g_refValueIn,l_motorOut) 
        motorcontrol.writeFrameShort(stm32Serial,'A',[int(g_motorIn)])


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
    global g_refValueIn
    global g_data1
    global data1Cnt
    print('press', event.key) #h=int16
    sys.stdout.flush()
    g_data1.clear() 
    if event.key == 'a':
        g_refValueIn=REF_VALUE_MAX
        pass
    elif event.key == 'b':
        g_refValueIn=REF_VALUE_MIN
        pass
    elif event.key == '+':
        g_pidP=g_pidP+1
    elif event.key == '-':
        g_pidP=g_pidP-1
    #do not uncomment
    # (add a delay at the beginning)   
    #updateGraph

motorcontrol.onNewFrameCommandCallback=onNewFrameCommand
motorcontrol.onNewFrameByteCallback=onNewFrameByte
motorcontrol.onNewFrameShortCallback=onNewFrameShort
motorcontrol.onNewFrameIntCallback=onNewFrameInt
motorcontrol.onNewFrameFloatCallback=onNewFrameFloat


#Open serial port
stm32Serial=motorcontrol.openSerialSTM32()

#create empty list
g_data1=[]

motor=0
g_refValueIn=REF_VALUE_MIN
g_pidP=1

stop_threads = False
t1 = threading.Thread( target=protocolThread,args =(lambda : stop_threads,))
t1.start()

# Display main figure
graphMain()

stop_threads=True
t1.join()
  
stm32Serial.close()

