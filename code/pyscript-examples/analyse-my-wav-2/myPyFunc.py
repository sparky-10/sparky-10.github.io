
# Class to 'analyse' an audio input signal
# Basic example used for demo purposes - lacking some basic error checking etc.

import numpy as np

# Defaults
FS_DEFAULT = 44100
NTRIM_DEFAULT = int(1e6) # Made up - bit over 20 seconds at e.g. 44.1 kHz sample rate
THRESHOLD_DEFAULT = 0.5

class myPyFunc:
    
    '''
    Class to 'analyse' an audio input signal
    '''
    
    def __init__(self):
        
        '''
        Initialise
        '''
        
        # Defaults (i.e. no input)
        self.yIn = None
        self.yInMono = None
        self.fs = None
        self.NChan = None
        self.N = None
    
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
        # Trim if needed
        NTrim = int(NTrim)
        if self.N > NTrim:
            self.yIn = self.yIn[0:NTrim,]
            self.N = NTrim
            self.trimmed = True
        else:
            self.trimmed = False
        # Get mono version of signal
        if self.NChan == 1:
            self.yInMono = self.yIn.copy()
        else:
            self.yInMono = np.mean(self.yIn, axis=-1)
            
        # Empty results
        self.overThreshold = None
        self.samplesOverThreshold = None
        self.percentOverThreshold = None
        self.overThresholdMono = None
        self.samplesOverThresholdMono = None
        self.percentOverThresholdMono = None
            
    def analyseInput(self, threshold=THRESHOLD_DEFAULT, doMultiChan=False, doMono=True):
        
        '''
        Analyse the signal
        Get part of signal above a given threshold
        '''
        
        # Analysis function (internal to this def)
        def overThreshold(y, threshold):
            return abs(y) >= threshold
        
        # If input is not empty...
        if not self.yIn is None:
            # If doing mono...
            if doMono:
                # Analyse the signal
                self.overThresholdMono = overThreshold(self.yInMono, threshold)
                self.samplesOverThresholdMono = np.sum(self.overThresholdMono)
                self.percentOverThresholdMono = 100.0*self.samplesOverThresholdMono/self.N
            # If doing individual channels
            if doMultiChan:
                # Empty outputs
                self.overThreshold = np.zeros([self.N, self.NChan])
                if self.NChan == 1 and doMono:
                    # Multi channel is same as mono (but in array)
                    self.overThreshold[:,0] = self.overThresholdMono   
                else:
                    # Do per channel
                    for i in range(self.NChan):
                        # This channel
                        if self.NChan > 1: yIn = self.yIn[:,i]
                        else: yIn = self.yIn
                        # Analyse the signal
                        self.overThreshold[:,i] = overThreshold(yIn, threshold)
                # Percentage over threshold
                self.samplesOverThreshold = np.sum(self.overThreshold, axis=0)
                self.percentOverThreshold = 100.0*self.samplesOverThreshold/self.N


