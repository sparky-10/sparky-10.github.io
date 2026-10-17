
# Class to 'analyse' an audio input signal
# Basic example used for demo purposes - lacking some basic error checking etc.

import numpy as np

# Defaults
FS_DEFAULT = 44100
NTRIM_DEFAULT = int(1e6) # Made up - bit over 20 seconds at e.g. 44.1 kHz sample rate

class myPyFunc:
    
    '''
    Class to 'analyse' an audio input signal
    '''
    
    def __init__(self):
        
        '''
        Initialise
        '''
        
        # Defaults (i.e. no input yet)
        self.yIn = None
        self.fs = None
    
    def setInput(self, yIn, fs=FS_DEFAULT, NTrim=NTRIM_DEFAULT):
        
        '''
        Set the input signal
        '''
        
        # Input and sample rate
        self.yIn = yIn
        self.fs = fs
        # Get size
        inputSize = self.yIn.shape
        self.N = inputSize[0]
        if len(inputSize) > 1:
            self.NChan = inputSize[1]
        else:
            self.NChan = 1
        # Length in seconds
        self.T = self.N/self.fs
        # Make mono (only one channel handled here)
        if len(inputSize) > 1:
            self.yIn = np.mean(self.yIn, axis=-1)
        # Trim if needed
        NTrim = int(NTrim)
        if self.N > NTrim:
            self.yIn = self.yIn[0:NTrim,]
            self.N = NTrim
            self.trimmed = True
        else:
            self.trimmed = False
            
    def analyseInput(self):
        
        '''
        Analyse the signal
        '''
        
        # No result as default
        self.rms = None
        self.maxAbs = None
        # If we have an input...
        if not self.yIn is None:
            # Analyse the signal
            self.rms = np.sqrt(np.mean(self.yIn**2))
            self.maxAbs = np.max(np.abs(self.yIn))

