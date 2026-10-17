from pyscript import when, document, display, HTML
import numpy as np
import matplotlib.pyplot as plt
import io
import scipy.io.wavfile as wavfile
from scipy.fft import fft
from ps_tools import fileUpload, fileDownload, printToDebug, pcm2float, getURLParams, sendCustomEvent
from ps_tools import constrainInputValue as constrainValue
from myPyFunc import myPyFunc

# Some basic settings
DEBUG = False                       # If printing to debug console (use integers to for verbosity level
DEBUG_PREFIX = "PY"                 # Prefix for identifying messages in debug console
STATUS_PREFIX = "Status: "          # Prefix for on screen status update
OP_FILENAME = "myNewWavFile.wav"    # Default filename for download
N_TRIM = int(1e6)                   # Max number of input samples to keep (just so we have a limit on the length to process)
FILTER_MIN_FREQ = 10                # Minimum frequency (Hz) for filter cut-off frequencies (unless sample rate is too low for this)
FILTER_MAX_FREQ = 22000             # Maximum frequency (Hz) for filter cut-off frequencies (unless sample rate is too low for this)

# Get some HTML elements by their id (don't need to do it this way, but it can be tidier)
statusUpdateElement = document.getElementById("statusUpdateId")
uploadButtonElement = document.getElementById("uploadButtonId")
downloadButtonElement = document.getElementById("downloadButtonId")
processButtonElement = document.getElementById("processButtonId")
filterTypeElement = document.getElementById("filterTypeId")
filterOrderElement = document.getElementById("filterOrderId")
filterFLowerElement = document.getElementById("filterFLowerId")
filterFUpperElement = document.getElementById("filterFUpperId")

# Print status update to screen
def printStatusUpdate(txt):
    statusUpdateElement.innerText = STATUS_PREFIX + txt
# Initial status
printStatusUpdate("Loading...")

# Get any 'presets' from URL
# Note: mostly error checked, but we could receive any kind of string so need to take care!!!
# Do DEBUG first...
val = getURLParams("DEBUG")
if not val is None:
    DEBUG = int(val)    # We assume debug is an int for use with verbosity level
    printToDebug("URL setting - DEBUG = %i"%DEBUG, DEBUG, DEBUG_PREFIX, verbosityLevel=2)
# Then do rest, so any possible URL input changes to DEBUG will have an effect
val = getURLParams("N_TRIM")
if not val is None:
    N_TRIM = int(val)
    N_TRIM = int(min(max(N_TRIM,10),1e8))
    printToDebug("URL setting - N_TRIM = %i"%N_TRIM, DEBUG, DEBUG_PREFIX, verbosityLevel=2)
val = getURLParams("filterType")
if not val is None:
    filterTypeElement.selectedIndex = int(val)
    filterTypeElement.selectedIndex = int(min(max(N_TRIM,0),3))
    txt = filterTypeElement.options[filterTypeElement.selectedIndex].innerText
    printToDebug("URL setting - filterType = %s"%txt, DEBUG, DEBUG_PREFIX, verbosityLevel=2)
val = getURLParams("filterOrder")
if not val is None:
    filterOrderElement.value = int(val)
    constrainValue(filterOrderElement, doStep = True)
    printToDebug("URL setting - filterOrder = %i"%int(filterOrderElement.value), DEBUG, DEBUG_PREFIX, verbosityLevel=2)
val = getURLParams("filterFLower")
if not val is None:
    filterFLowerElement.value = float(val)
    constrainValue(filterFLowerElement)
    printToDebug("URL setting - filterFLower = %f"%float(filterFLowerElement.value), DEBUG, DEBUG_PREFIX, verbosityLevel=2)
val = getURLParams("filterFUpper")
if not val is None:
    filterFUpperElement.value = float(val)
    constrainValue(filterFUpperElement)
    printToDebug("URL setting - filterFUpper = %f"%float(filterFUpperElement.value), DEBUG, DEBUG_PREFIX, verbosityLevel=2)

# Disable buttons that shouldn't be used until we're ready
uploadButtonElement.disabled = False
downloadButtonElement.disabled = True
processButtonElement.disabled = True

# Initialise filtering object
myPyFuncObj = myPyFunc()

# Trigger on upload input change
@when("change", "#uploadWavId")
async def uploadAudio(event):
    '''
    Await file upload, then load and st then plot input signal
    '''
    # Print to debug and screen
    printToDebug("File upload", DEBUG, DEBUG_PREFIX)
    printStatusUpdate("File upload...")
    # Await getting file - i.e. loading to virtual file system
    filename = await fileUpload(event)
    # If we have a file...
    if len(filename) > 0:
        # File is first file (regardless of if more than one file was selected) 
        filename = filename[0]
        # print to debug
        printToDebug("Reading filename = %s"%filename, DEBUG, DEBUG_PREFIX, verbosityLevel=2)
        # Read data
        (fs, yIn) = wavfile.read(filename)
        # In case received PCM integer data make float
        yIn = pcm2float(yIn)
        # Set the input in the filtering object
        myPyFuncObj.setInput(yIn, fs, N_TRIM)
        # Set filter frequency limits (I.e. cut-off frequencies should be no more than Nyquist)
        setFilterFreqLimits(fs*0.5)
        # Make the plot
        makePlot()
        # Enable processing button (but not download yet)
        downloadButtonElement.disabled = True
        processButtonElement.disabled = False
        # Print to debug (and let user know max size of processed audio if trimmed)
        updateStr = "File upload finished"
        if myPyFuncObj.trimmed:
            updateStr += " (note: input trimmed to max N = %i samples)"%N_TRIM
        printStatusUpdate(updateStr)

def setFilterFreqLimits(fUpLim=float('inf')):
    '''
    Set filter frequency inputs to within limits that make sense
    '''
    # Print to debug
    printToDebug("Set filter freq. limits", DEBUG, DEBUG_PREFIX, verbosityLevel=2)
    # Set limits to minimum of value passed and default min/max limits
    filterFLowerElement.min = min(FILTER_MIN_FREQ,fUpLim)
    filterFUpperElement.min = min(FILTER_MIN_FREQ,fUpLim)
    filterFLowerElement.max = min(FILTER_MAX_FREQ,fUpLim)
    filterFUpperElement.max = min(FILTER_MAX_FREQ,fUpLim)
    # Constrain values to within new limits
    constrainValue(filterFLowerElement)
    constrainValue(filterFLowerElement)

# Trigger on download button click
@when("click", "#downloadButtonId")
def downloadAudio(event):
    '''
    Download audio
    '''
    # Print to debug and screen
    printToDebug("File download", DEBUG, DEBUG_PREFIX)
    printStatusUpdate("File download")
    # If we have an output
    if not myPyFuncObj.yOut is None:
        # Write to memory using BytesIO
        opFile = io.BytesIO()
        wavfile.write(opFile, myPyFuncObj.fs, myPyFuncObj.yOut)
        # Trigger file download as an "audio/wav" type (including prints to debug and screen)
        printToDebug("Download triggered with filename = %s"%OP_FILENAME, DEBUG, DEBUG_PREFIX, verbosityLevel=2)
        fileDownload(OP_FILENAME, opFile, "audio/wav")
        printStatusUpdate("File download finished")

# Trigger on any filter type change
@when("change", "#filterTypeId")
def filterTypeChange(event):
    '''
    Edit page elements according to filter type selected
    (i.e. enable/disable lower/upper frequency input boxes)
    '''
    # Print to debug and screen
    printToDebug("Filter type change", DEBUG, DEBUG_PREFIX)
    printStatusUpdate("Ready")
    # Get filter type and cut-off frequencies
    filterTypeIndex = filterTypeElement.selectedIndex
    filterType =  filterTypeElement.options[filterTypeIndex].text
    # Enable/disable user control of filter cut-off frequencies according to filter type
    if filterType == "Low pass":
        filterFLowerElement.disabled = True
    else:
        filterFLowerElement.disabled = False
    if filterType == "High pass":
        filterFUpperElement.disabled = True
    else:
        filterFUpperElement.disabled = False
    # Print to debug
    printToDebug("Filter type = %s"%filterType, DEBUG, DEBUG_PREFIX, verbosityLevel=2)

# Trigger on any filter order change
@when("change", "#filterOrderId")
def filterOrderChange(event):
    '''
    Process filter order change
    '''
    # Print to debug and screen
    printToDebug("Filter order change", DEBUG, DEBUG_PREFIX)
    printStatusUpdate("Ready")
    # Make sure any entered value is within min/max limits
    constrainValue(event, doStep = True)
    # print to debug
    printToDebug("Filter order = %i"%int(filterOrderElement.value), DEBUG, DEBUG_PREFIX, verbosityLevel=2)

# Trigger on any filter lower frequency change
@when("change", "#filterFLowerId")
def filterFLowerChange(event):
    '''
    Process filter cut-off frequencies on lower frequency change
    '''
    # Print to debug and screen
    printToDebug("Filter lower freq. change", DEBUG, DEBUG_PREFIX)
    printStatusUpdate("Ready")
    # Make sure any entered value is within min/max limits
    constrainValue(event)
    # Make sure upper value is not lower than lower
    fLow = float(filterFLowerElement.value)
    fUp = float(filterFUpperElement.value)
    if fLow > fUp:
        filterFUpperElement.value = fLow
    # print to debug
    printToDebug("f Lower = %f Hz"%fLow, DEBUG, DEBUG_PREFIX, verbosityLevel=2)
    printToDebug("f Upper = %f Hz"%fUp, DEBUG, DEBUG_PREFIX, verbosityLevel=2)

# Trigger on any filter upper frequency change
@when("change", "#filterFUpperId")
def filterFUpperChange(event):
    '''
    Process filter cut-off frequencies on upper frequency change
    '''
    # Print to debug and screen
    printToDebug("Filter upper freq. change", DEBUG, DEBUG_PREFIX)
    printStatusUpdate("Ready")
    # Make sure any entered value is within min/max limits
    constrainValue(event)
    # Make sure lower value is not higher than upper
    fLow = float(filterFLowerElement.value)
    fUp = float(filterFUpperElement.value)
    if fUp < fLow:
        filterFLowerElement.value = fUp
    # print to debug
    printToDebug("f Lower = %f Hz"%fLow, DEBUG, DEBUG_PREFIX, verbosityLevel=2)
    printToDebug("f Upper = %f Hz"%fUp, DEBUG, DEBUG_PREFIX, verbosityLevel=2)

# Trigger on process button click
@when("click", "#processButtonId")
def processAudio(event):
    '''
    Get settings, process (filter) audio, and plot
    '''
    # Print to debug and screen
    printToDebug("Processing audio", DEBUG, DEBUG_PREFIX)
    printStatusUpdate("Processing...")
    # Get filter order from page
    fOrder = int(filterOrderElement.value)
    # Get filter type and cut-off frequencies
    filterTypeIndex = filterTypeElement.selectedIndex
    filterType =  filterTypeElement.options[filterTypeIndex].text
    match filterType:
        case "Low pass":
            fType = "lowpass"
            fCut = float(filterFUpperElement.value)
        case "High pass":
            fType = "highpass"
            fCut = float(filterFLowerElement.value)
        case "Band pass":
            fType = "bandpass"
            fCut = [float(filterFLowerElement.value), float(filterFUpperElement.value)]
        case "Band stop":
            fType = "bandstop"
            fCut = [float(filterFLowerElement.value), float(filterFUpperElement.value)]
    # Filter input using obtained settings
    myPyFuncObj.filterInput(fOrder=fOrder, fCut=fCut, fType=fType)
    # Remake plot with input and output
    makePlot()
    # Enable download button
    downloadButtonElement.disabled = False
    # Update status
    printStatusUpdate("Processing finished")

def makePlot():
    '''
    # Make plot(s) and add to page
    '''
    # Print to debug and screen
    printToDebug("Making plot", DEBUG, DEBUG_PREFIX)
    printStatusUpdate("Plotting...")
    # Create plots
    #fig1, axs1 = plt.subplots(myPyFuncObj.NChan, 1, figsize=(6, 3))
    #fig2, axs2 = plt.subplots(myPyFuncObj.NChan, 1, figsize=(6, 3))
    fig1, axs1 = plt.subplots(myPyFuncObj.NChan, 1)
    fig2, axs2 = plt.subplots(myPyFuncObj.NChan, 1)
    # Plot data (if we have data)...
    if not myPyFuncObj.yIn is None:
        # Input time and frequency data
        N = myPyFuncObj.N
        fs = myPyFuncObj.fs
        T = (N-1)/fs
        F = fs*(N-1)/N
        t = np.linspace(0, T, N)
        f = np.linspace(0, F, N)
        # Plot input data for each channel
        for i in range(myPyFuncObj.NChan):
            # Get input data and axes to plot to
            if myPyFuncObj.NChan > 1:
                yIn = myPyFuncObj.yIn[:,i]
                ax1 = axs1[i] # Yes, this is clumsy/ugly!!
                ax2 = axs2[i]
            else:
                yIn = myPyFuncObj.yIn
                ax1 = axs1
                ax2 = axs2
            # Frequency domain data
            YIn = 20.0*np.log10(np.abs(fft(yIn)))
            # Plot to axes
            ax1.plot(t, yIn, 'b-', linewidth=1, label='Input')
            ax2.semilogx(f, YIn, 'b-', linewidth=1, label='Input')
            # Plot labels, limits etc...
            ax1.set_xlim(0, t[-1])
            ax1.set_xlabel('Time (s)')
            ax1.set_ylabel('Level')
            ax1.set_title('Channel #%i'%(i+1))
            ax1.grid()
            ax2.set_xlim(xmax=fs/2)
            ax2.set_xlabel('Frequency (Hz)')
            ax2.set_ylabel('Magnitude (dB)')
            ax2.set_title('Channel #%i'%(i+1))
            ax2.grid()
        # Add processed data (if there is any)...
        if not myPyFuncObj.yOut is None:
            for i in range(myPyFuncObj.NChan):
                # As above...
                if myPyFuncObj.NChan > 1:
                    yOut = myPyFuncObj.yOut[:,i]
                    ax1 = axs1[i] # Yes, this is clumsy/ugly!!
                    ax2 = axs2[i]
                else:
                    yOut = myPyFuncObj.yOut
                    ax1 = axs1
                    ax2 = axs2
                YOut = 20.0*np.log10(np.abs(fft(yOut)))
                ax1.plot(t, yOut, 'r--', linewidth=1, label='Output')
                ax2.semilogx(f, YOut, 'r--', linewidth=1, label='Output')
        # Put legends in upper right (note: use of default "best" can cause errors due to being too slow)
        ax1.legend(loc="upper right")
        ax2.legend(loc="upper right")
        # 'Adjust the padding between and around subplots'
        fig1.tight_layout()
        fig2.tight_layout()
        # Display plots including html heading labels
        display(HTML("<h3>Time domain</h3>"), target="plotDivLId", append=False)
        display(HTML("<h3>Frequency domain</h3>"), target="plotDivRId", append=False)
        display(fig1, target="plotDivLId")
        display(fig2, target="plotDivRId")
    # Delete plot handles when finished
    plt.close(fig1)
    plt.close(fig2)

# Run this so appropriate filter type changes are applied on loading (i.e. enable/disable relevant filter freqs from any user input)
filterTypeChange(None)

# Print to debug (let know we're at the end of the code)
# Note: verbosityLevel=0 means print even if debug messages turned off
printToDebug("End of PyScript code", DEBUG, DEBUG_PREFIX, verbosityLevel=0)

# Update status
printStatusUpdate("Ready")

# Send custom event (with name being listened for to close splash screen)
# Note we could just do this manually - e.g. document.getElementById('loadingDiv').close() - but this is more satisfying!
sendCustomEvent("py:loaded")

