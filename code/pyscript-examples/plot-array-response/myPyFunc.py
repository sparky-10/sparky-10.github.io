
# Class to calculate the far-field directivity of a linear line array of N sources 
# Basic example used for demo purposes - lacking some basic error checking etc.

from ps_tools import printToDebug, editDebugPrefix
import numpy as np

# Defaults
DEBUG = False
DEBUG_PREFIX = ""
VERBOSITY_LEVEL = 1
A_DEFAULT = np.ones(2)
DX_DEFAULT = 0.1
F_DEFAULT = 1000

class myPyFunc:

    '''
    Class to calculate the far-field directivity of a linear line array of N sources
    '''
    
    def __init__(self, 
                 debug=DEBUG, 
                 debugPrefix=DEBUG_PREFIX,
                 verbosityLevel=VERBOSITY_LEVEL):
        
        '''
        Initialise
        '''
        
        # For debug
        self.debugOptions = editDebugPrefix({
            "debug":debug, 
            "debugPrefix":debugPrefix, 
            "verbosityLevel":verbosityLevel
            })
        
        # Print to debug
        printToDebug("Setting defaults", **self.debugOptions)
        
        # Defaults on init
        self.c0 = 344
        self.nTheta = 180*4+1
        self.theta = np.linspace(-90, 90, self.nTheta)
        self.p = None
    
    def updateDirectivity(self, A=A_DEFAULT, dx=DX_DEFAULT, f=F_DEFAULT):
        
        '''
        Calculate directivity
        '''
        
        # Print to debug
        printToDebug("Calculating directivity", **self.debugOptions)
        
        # Inputs
        N = len(A)
        k = 2*np.pi*f/self.c0
        
        # Loop round and sum to get output
        self.p = np.zeros(self.nTheta)
        for n, a in enumerate(A):
            self.p = self.p + a*np.exp(1j*n*k*dx*np.sin(np.deg2rad(self.theta)))

