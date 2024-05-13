#============================================================
# Motor control loop in python with simulated motor model
#     Author: F. CRISON
#     Version: 1.0.0
#============================================================
from time import sleep
import array
import sys
import numpy as np
import matplotlib.pyplot as plt
from motorSimu import MotorSimu

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
    outPid=l_epsilon*g_pidP
    return outPid
#============================================================



#============================================================
def getGraphTitleString():
    return ('Press a,b,-,+ P='+str(g_pidP))
def updateGraph():
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

def onNewFrameShort(p_frameCode:int,p_short:array):
    #On new motor output sample
    global g_pidP
    global g_data1
    global g_motorIn
    l_motorOut=p_short[0]
    if p_frameCode == ord('A'):
        if len(g_data1)<200:
            if (l_motorOut<-32000):
                l_motorOut=-32000
            if (l_motorOut>32000):
                l_motorOut=32000
            g_data1.append(l_motorOut)
        elif len(g_data1) == 200 :
            updateGraph()
        ##### CONTROL LOOP #####
        g_motorIn= controlLoop(g_refValueIn,l_motorOut) 

def on_key(event):
    global g_pidP
    global g_refValueIn
    global g_data1
    global g_motorIn
    #print('press', event.key)
    sys.stdout.flush()
    g_data1=array.array('h') #h=int16
    if event.key == 'a':
        g_refValueIn=REF_VALUE_MAX
        pass
    elif event.key == 'b':
        g_refValueIn=REF_VALUE_MIN
        pass
    elif event.key == '+':
        g_pidP=g_pidP+1
        updateGraph()
        return
    elif event.key == '-':
        if g_pidP>=2:
            g_pidP=g_pidP-1
        updateGraph()
        return
    else:
        return
    #########################
    # Control loop simulation
    #########################
    g_motorIn=0   
    for i in range(201):
        outMotor=motor.update(g_motorIn)
        onNewFrameShort( ord('A'), np.array( [int(outMotor*4.7)]))


######################################
#                                    #
#              MAIN                  #
#                                    #
######################################

# Set input reference value 
g_refValueIn=REF_VALUE_MAX
# Create simulated motor
motor=MotorSimu( REF_VALUE_MIN/4.7)
#Data graph
g_data1=array.array('h') #h=int16
# Set motor voltage input
g_motorIn=0
#pid 'P' parameter
g_pidP=1
# Display main figure
graphMain()




