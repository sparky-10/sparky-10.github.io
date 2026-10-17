from pyscript import when, document, window, fetch
import numpy as np
import scipy.io.wavfile as wavfile
from myPyFunc import myPyFunc

# Some basic settings
DEBUG = True                        # If printing to debug console
N_TRIM = int(1e6)                   # Max number of input samples to keep (just so we have a limit on the length to analyse)
THRESHOLD = 0.5                     # Threshold used for 'analysis'

# Get some HTML elements by their id (don't need to do it this way, but it can be tidier)
paraTrimElement = document.getElementById("paraTrimId")
uploadButtonElement = document.getElementById("uploadButtonId")
analyseButtonElement = document.getElementById("analyseButtonId")
filenameTableElement = document.getElementById("filenameTableId")
nChannelTableElement = document.getElementById("nChannelTableId")
sampleRateTableElement = document.getElementById("sampleRateTableId")
nSampleTableElement = document.getElementById("nSampleTableId")
timeLengthTableElement = document.getElementById("timeLengthTableId")
rmsTableElement = document.getElementById("rmsTableId")
maxAbsTableElement = document.getElementById("maxAbsTableId")

# Add text to page to let user know max size of audio used
# and print to console for debugging
if DEBUG: print("Add max samples allowed text to page")
paraTrimElement.innerText = "Page loaded (note: input trimmed to max N = %i samples)"%N_TRIM

# Initialise analysis object
myPyFuncObj = myPyFunc()

# Disable buttons that shouldn't be used immediately on page load
uploadButtonElement.disabled = False
analyseButtonElement.disabled = True

# Trigger on upload input change
@when("change", "#uploadWavId")
async def uploadAudio(event):
    '''
    Await file upload, then load and set page ready to analyse
    '''
    # Print to console for debugging
    if DEBUG: print("File upload")
    # Await getting file - i.e. loading to virtual file system
    filename = await fileUpload(event)
    # If we have a file...
    if len(filename) > 0:
        # Print to console for debugging
        if DEBUG: print("File read")
        # File is first file (regardless of if more than one file was selected) 
        filename = filename[0]
        # Read data from file
        (fs, yIn) = wavfile.read(filename)
        # In case received PCM integer data make float
        yIn = pcm2float(yIn)
        # Set the input in the analysis object
        myPyFuncObj.setInput(yIn, fs, N_TRIM)
        # Print filename and clear any previous results on page
        filenameTableElement.innerText = filename
        nChannelTableElement.innerText = ""
        sampleRateTableElement.innerText = ""
        nSampleTableElement.innerText = ""
        timeLengthTableElement.innerText = ""
        rmsTableElement.innerText = ""
        maxAbsTableElement.innerText = ""
        # Enable analysis button
        analyseButtonElement.disabled = False

async def fileUpload(event):
    """
    Upload file(s) onto the virtual file system
    Usually activate when user has selected a file to upload via the file input element
    See https://docs.pyscript.net/2026.7.3/faq/#loading-files
    """
    input = event.target
    filenames = []
    # For each file the user has selected to upload...
    for file in input.files:
        # Create a temporary URL.
        tmp = window.URL.createObjectURL(file)
        # Fetch and save its content somewhere.
        with open(f"./{file.name}", "wb") as dest:
            dest.write(await fetch(tmp).bytearray())
        # Then revoke the tmp URL.
        window.URL.revokeObjectURL(tmp)
        filenames.append(file.name)
    return filenames

# Trigger on analyse button click
@when("click", "#analyseButtonId")
def analyseAudio(event):
    '''
    Analyse the audio and print results to page
    '''
    # Print to console for debugging
    if DEBUG: print("Analysing audio")
    # Do signal analysis
    myPyFuncObj.analyseInput()
    # Add results to page
    printResultsToPage()

def printResultsToPage():
    '''
    Get results and add to page
    '''
    # Print to console for debugging
    if DEBUG: print("Print results to page")
    # Update page text
    nChannelTableElement.innerText = "%i"%myPyFuncObj.NChan
    sampleRateTableElement.innerText = "%i"%myPyFuncObj.fs
    nSampleTableElement.innerText = "%i"%myPyFuncObj.N
    timeLengthTableElement.innerText = "%0.4f"%myPyFuncObj.T
    rmsTableElement.innerText = "%0.4f"%myPyFuncObj.rms
    maxAbsTableElement.innerText = "%0.4f"%myPyFuncObj.maxAbs

# Convert PCM data to float
def pcm2float(y):
    '''
    Convert PCM data to float
    '''
    #  if data type not float (note: bit hacky, and not all data types handled)
    if y.dtype != np.dtype('float64'):
        # Assume data type received indicates standard PCM encoding
        if y.dtype == np.dtype('int8'):
            nbit = 8
        elif y.dtype == np.dtype('int16'):
            nbit = 16
        elif y.dtype == np.dtype('int32'):
            nbit = 32
        else:
            # we don't expect to get here
            print("WARNING: data type not handled")
        # Convert to float
        y = np.float64(y)*2**-(nbit-1)
    return y

# Print to console for debugging
# (so we know when we've reached the end of the code block)
if DEBUG: print("End of PyScript code")

