#============================================================
# Motor-gearbox-load discrete simulation (Fe=100Hz)
#     Author: F. CRISON
#     Version: 1.0.0
#============================================================
import numpy as np

class MotorSimu:

    def __init__(self, p_initPos:float) -> None:
        """Find serial port of connected STM32 board
        Parameters:
            p_initPos (float): initial motor output position
        Returns:
            None 
        """
        self.xn=np.array([0.0, 0.0, 0.0],dtype=np.float32)
        self.yn=np.array([p_initPos, p_initPos, p_initPos],dtype=np.float32)

    def update(self,p_motorIn:int):
        """Update motor position (to be called every 'Fe' Hz)
        Parameters:
            p_motorIn (float): motor input voltage (Volt)
        Returns:
            float : new motor position (Radian)
        """
        self.xn[0]=p_motorIn
        y=  (0.00025199*self.xn[2]) + (0.00050399*self.xn[1]) + (0.00025199*self.xn[0])
        y=y - (0.94681*self.yn[2]) + (1.94681*self.yn[1])
        self.yn[0]=y
        self.xn[2]=self.xn[1]
        self.xn[1]=self.xn[0]
        self.yn[2]=self.yn[1]
        self.yn[1]=self.yn[0]
        return self.yn[0]
            
        pass 