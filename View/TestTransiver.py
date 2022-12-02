import numpy as np
from scipy import signal

class TestTranciver():
    def __init__(self):
        self.T = 0
    
    def Transmit(self,step_id):
        #  допустим на передачу синус
        fs = 192e3
        dt = 1/fs
        pi = np.pi
        Un = 100

        f0 = 40000
        f1 = 5000
        m=0.3
        testSig = Un*np.cos(2*pi*dt*step_id/self.T)
        # testSig = Un*(1+m*np.cos(2*pi*f1*dt*step_id))*np.cos(2*pi*f0*dt*step_id)
        return [dt*step_id,testSig]
    
    def Reciev(self,step_id):
        fs = 192e3
        dt = 1/fs
        Un = 100
        if (dt*step_id % self.T)<self.T/2:
            testSig = -Un+Un*2*(dt*step_id % self.T)/self.T
        else:
            testSig = Un-Un*2*(dt*step_id % self.T)/self.T
        return [dt*step_id,testSig]