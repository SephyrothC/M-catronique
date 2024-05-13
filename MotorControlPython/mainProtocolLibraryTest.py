#============================================================
# Protocol library test 
#     Author: F. CRISON
#     Version: 1.0.0
#============================================================
import motorcontrol

#Library test
stm32Serial=motorcontrol.openSerialSTM32()
motorcontrol.protocolLibraryTest(stm32Serial)
stm32Serial.close()



