
# Class to filter an audio input signal
# Basic example used for demo purposes - lacking some basic error checking etc.

from scipy import signal
import numpy as np

# Defaults
FS_DEFAULT = 44100          # Sample rate (Hz)
FORDER_DEFAULT = 2          # Filter order
FCUT_DEFAULT = 500          # Filter cut-off frequency/frequencies (Hz)
FTYPE_DEFAULT = "lowpass"   # Filter type
NTRIM_DEFAULT = int(1e6)    # Made up - bit over 20 seconds at e.g. 44.1 kHz sample rate

class myPyFunc:

    '''
    Class to filter  an audio input signal
    '''
    
    def __init__(self):
        
        '''
        Initialise
        '''
        
        # Defaults (i.e. no input yet)
        self.yIn = None
        self.yOut = None
        self.fs = None
    
    def setInput(self, yIn, fs=FS_DEFAULT, NTrim=NTRIM_DEFAULT):
        
        '''
        Set the input signal
        '''
        
        # Input, empty output, and sample rate
        self.yIn = yIn
        self.yOut = None
        self.fs = fs
        # Get size
        inputSize = self.yIn.shape
        self.N = inputSize[0]
        if len(inputSize) > 1:
            self.NChan = inputSize[1]
        else:
            self.NChan = 1
        # Trim if needed
        NTrim = int(NTrim)
        if self.N > NTrim:
            self.yIn = self.yIn[0:NTrim,]
            self.N = NTrim
            self.trimmed = True
        else:
            self.trimmed = False
    
    def getOutput(self):
        
        '''
        Get the output signal
        '''
        
        # Just return what's stored in self
        return self.yOut
        
    def filterInput(self, fOrder = FORDER_DEFAULT, fCut = FCUT_DEFAULT, fType = FTYPE_DEFAULT):
        
        '''
        Filter the signal
        '''
        
        # If there's an input...
        if not self.yIn is None:
            # Define filter and apply
            sos = signal.butter(fOrder, fCut, btype=fType, fs=self.fs, output='sos')
            self.yOut = signal.sosfilt(sos, self.yIn, axis=0)
        else:
            # No output if no input
            self.yOut = None
        # Return result
        return self.yOut

