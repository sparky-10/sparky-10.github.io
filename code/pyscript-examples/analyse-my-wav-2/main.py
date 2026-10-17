from pyscript import when, document, display
import numpy as np
import matplotlib.pyplot as plt
#import scipy.io.wavfile as wavfile
import soundfile as sf
from ps_tools import fileUpload, printToDebug, pcm2float
from ps_tools import constrainInputValue as constrainValue
from myPyFunc import myPyFunc
 
# Some basic settings
DEBUG = True                        # If printing to debug console
DEBUG_PREFIX = "PY"                 # Prefix for identifying messages in debug console
STATUS_PREFIX = "Status: "          # Prefix for on screen status update
N_TRIM = int(1e6)                   # Max number of input samples to keep (just so we have a limit on the length to analyse)
THRESHOLD = 0.5                     # Threshold used for 'analysis'

# Get some HTML elements by their id (don't need to do it this way, but it can be tidier)
statusUpdateElement = document.getElementById("statusUpdateId")
uploadButtonElement = document.getElementById("uploadButtonId")
analyseButtonElement = document.getElementById("analyseButtonId")
analysisThresholdElement = document.getElementById("analysisThresholdId")
filenameTableDataElement = document.getElementById("filenameTableDataId")
nChannelTableDataElement = document.getElementById("nChannelTableDataId")
sampleRateTableDataElement = document.getElementById("sampleRateTableDataId")
nSampleTableDataElement = document.getElementById("nSampleTableDataId")
timeLengthTableDataElement = document.getElementById("timeLengthTableDataId")
rmsTableDataElement = document.getElementById("rmsTableDataId")
maxAbsTableDataElement = document.getElementById("maxAbsTableDataId")
signalStatsTableElement = document.getElementById("signalStatsTableId")

# Print status update to screen
def printStatusUpdate(txt):
    statusUpdateElement.innerText = STATUS_PREFIX + txt
# Initial status
printStatusUpdate("Loading...")

# Initialise filtering object
myPyFuncObj = myPyFunc()

# Disable buttons that shouldn't be used until we're ready
uploadButtonElement.disabled = False
analyseButtonElement.disabled = True

# Trigger on upload input change
@when("change", "#uploadWavId")
async def uploadAudio(event):
    '''
    Await file upload, then load and set page ready to analyse
    '''
    # Print to debug and screen
    printToDebug("File upload", DEBUG, DEBUG_PREFIX)
    printStatusUpdate("File upload...")
    # Await getting file - i.e. loading to virtual file system
    filename = await fileUpload(event)
    # If we have a file...
    if len(filename) > 0:
        # Print to debug
        printToDebug("File read", DEBUG, DEBUG_PREFIX)
        # File is first file (regardless of if more than one file was selected) 
        filename = filename[0]
        # Read data
        #(fs, yIn) = wavfile.read(filename)
        (yIn, fs) = sf.read(filename)       # use soundfile for reading .wav
        # In case received PCM integer data make float
        yIn = pcm2float(yIn)
        # Set the input in the analysis object
        myPyFuncObj.setInput(yIn, fs, N_TRIM)
        # Initialise table(s) - clear any previous results on page and print filename
        initTable(filename)
        # Make the plot
        makePlot()
        # Enable analyse button
        analyseButtonElement.disabled = False
        # Print to debug (and let user know max size of processed audio if trimmed)
        updateStr = "File upload finished"
        if myPyFuncObj.trimmed:
            updateStr += " (note: input trimmed to max N = %i samples)"%N_TRIM
        printStatusUpdate(updateStr)

# Trigger on any analysis threshold change
@when("change", "#analysisThresholdId")
def analysisThresholdChange(event):
    '''
    Tidy up after get threshold change
    '''
    # Print to debug and screen
    printToDebug("Analysis threshold change", DEBUG, DEBUG_PREFIX)
    printStatusUpdate("Ready")
    # Make sure any entered value is within min/max limits
    constrainValue(event, doStep = True)

# Trigger on analyse button click
@when("click", "#analyseButtonId")
def analyseAudio(event):
    '''
    Analyse audio and update page results and plot
    '''
    # Print to debug and screen
    printToDebug("Analysing audio", DEBUG, DEBUG_PREFIX)
    printStatusUpdate("Analysing...")
    # Get analysis threshold from page
    threshold = float(analysisThresholdElement.value)
    # Do signal analysis
    doMultiChan = True
    doMono = True
    myPyFuncObj.analyseInput(threshold=threshold, doMultiChan=doMultiChan, doMono=doMono)
    # Add results to page
    printMultiChan = True
    printMono = myPyFuncObj.NChan > 1   # Only print mono if have more than one channel
    printResultsToPage(printMultiChan=printMultiChan, printMono=printMono)
    # Remake plot
    makePlot()
    # Update status
    printStatusUpdate("Analysis finished")

def initTable(filename=""):
    '''
    Clear/reset table(s) and add filename if passed
    '''
    # Update file properties table
    filenameTableDataElement.innerText = filename
    nChannelTableDataElement.innerText = ""
    sampleRateTableDataElement.innerText = ""
    nSampleTableDataElement.innerText = ""
    timeLengthTableDataElement.innerText = ""
    # Update signal stats table
    for row in signalStatsTableElement.rows:
        # For each row - clear data in second column and remove any following columns
        cols = row.cells
        NCols = len(cols)
        cols[1].innerText = ""
        for i in range(NCols-2):
            row.deleteCell(-1)
    
def printResultsToPage(printMultiChan, printMono):
    '''
    # Get results and add to page
    '''
    # Print to debug
    printToDebug("Print results to page", DEBUG, DEBUG_PREFIX)
    # Add file properties
    nChannelTableDataElement.innerText = "%i"%myPyFuncObj.NChan
    sampleRateTableDataElement.innerText = "%i"%myPyFuncObj.fs
    nSampleTableDataElement.innerText = "%i"%myPyFuncObj.N
    timeLengthTableDataElement.innerText = "%0.4f"%myPyFuncObj.T
    # Add signal stats
    # For each row - add any columns if needed...
    numColsNeeded = 1 + int(printMono) + int(printMultiChan)*myPyFuncObj.NChan
    for row in signalStatsTableElement.rows:
        cols = row.cells
        NCols = len(cols)
        addNCols = numColsNeeded-NCols
        for i in range(addNCols):
            row.insertCell(-1)
    # Rows we want to edit
    rows = signalStatsTableElement.rows
    # If doing multichannel, set NChan columns
    if printMultiChan:
        for i in range(myPyFuncObj.NChan):
            rows[0].cells[i+1].innerText = i+1
            rows[1].cells[i+1].innerText = "%i"%myPyFuncObj.samplesOverThreshold[i]
            rows[2].cells[i+1].innerText = "%0.2f"%myPyFuncObj.percentOverThreshold[i]
    # If doing mono, set end column
    if printMono:
        rows[0].cells[-1].innerText = "'Mono'"
        rows[1].cells[-1].innerText = "%i"%myPyFuncObj.samplesOverThresholdMono
        rows[2].cells[-1].innerText = "%0.2f"%myPyFuncObj.percentOverThresholdMono

# Make plot(s) and add to page
def makePlot():
    '''
    Make the plot
    '''
    # Print to debug and screen
    printToDebug("Making plot", DEBUG, DEBUG_PREFIX)
    printStatusUpdate("Plotting...")
    # Create plot
    fig, ax = plt.subplots()
    # Plot data (if we have data)...
    if not myPyFuncObj.yIn is None:
        # Input time and frequency data
        N = myPyFuncObj.N
        fs = myPyFuncObj.fs
        T = (N-1)/fs
        t = np.linspace(0, T, N)
        # Plot input data (use mono signal)
        ax.plot(t, myPyFuncObj.yInMono, 'b-', linewidth=1, label='Input')
        # Plot labels, limits etc...
        ax.set_xlim(0, t[-1])
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Level')
        ax.set_title('Mono signal')
        ax.grid()
        # Add analysis data (if there is any)...
        if not myPyFuncObj.overThresholdMono is None:
            # Use masked version of signal (positive and negative) 
            yOverThresholdUpper = np.ma.masked_where(
                np.logical_or(myPyFuncObj.overThresholdMono == False, myPyFuncObj.yInMono <= 0), 
                myPyFuncObj.yInMono)
            yOverThresholdLower = np.ma.masked_where(
                np.logical_or(myPyFuncObj.overThresholdMono == False, myPyFuncObj.yInMono >= 0), 
                myPyFuncObj.yInMono)
            # Add to plot
            ax.plot(t, yOverThresholdUpper, 'r.--', linewidth=1, label='Above threshold')
            ax.plot(t, yOverThresholdLower, 'r.--', linewidth=1)
        # Put legend in upper right (note: use of default "best" can cause errors due to being too slow)
        ax.legend(loc="upper right")
        # Display plot(s) (append False to overwrite any previous content)
        display(fig, target="plotDivId", append=False)
    # Delete plot handles(s) when finished
    plt.close(fig)

# Print to screen (let know we're at the end of the code)
printToDebug("End of PyScript code", DEBUG, DEBUG_PREFIX)

# Update status
printStatusUpdate("Ready")

