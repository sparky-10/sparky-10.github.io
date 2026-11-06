import time

# Simple very quick block of code
def quickCalc(a, b):
    return a + b
    
# Time consuming (and blocking) code
def slowCalc(a, b):
    time.sleep(5)   # Block for 5 seconds
    return a + b

# Return function for use outside worker
__export__ = ["quickCalc", "slowCalc"]


