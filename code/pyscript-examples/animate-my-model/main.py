from pyscript import when, document, window
import numpy as np
from ps_tools import printToDebug, initElement, setURLParams, sendCustomEvent, fileDownload
from ps_tools import sendEvent 
from ps_tools import constrainInputValue as constrainValue
import plotly.graph_objs as plotly_go
import plotly.utils
import json
from pyFDTD import pyFDTD
import scipy.io.wavfile as wavfile
import io
import asyncio

# Some basic settings
DEBUG = False                       # If printing to debug console (use integers to for verbosity level)
DEBUG_PREFIX = "PY"                 # Prefix for identifying messages in debug console
STATUS_PREFIX = "Status: "          # Prefix for on screen status update
OP_FILENAME = "myNewWavFile.wav"    # Default filename for download
plotPauseTime = 1e-3                # Plot update pause time
gridLength = 1.0                    # length of grid (m)

# Set parameters received from URL - Do DEBUG first separately so affects everything else that follows
# CAUTION: ALLOWS SETTING OF GLOBAL VARIABLES!!!!!!!!!!
setURLParams({"DEBUG":int}, varSpace=globals(), debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=0)

# Print status update to screen
statusUpdate = initElement(id="statusUpdateId")
def printStatusUpdate(txt):
    statusUpdate.innerText = STATUS_PREFIX + txt

# Initial status
printStatusUpdate("Loading...")

# URL settable parameters that we allow, and their data types/limits for setting
URLParamsAllowed = {}
# E.g. append URL with ?gridDistance.value=5&gridStepSize=0.0025&sourcePosition.value=2
URLParamsAllowed = {
    "gridDistance.value":float,
    "gridDistance.min":{"type":float, "min":0.01, "max":1},
    "gridDistance.max":{"type":float, "min":1.0, "max":100},
    "gridDistance.step":{"type":float, "min":0.01, "max":1},
    "gridStepSize.value":float,
    "gridStepSize.min":{"type":float, "min":0.0001, "max":0.01},
    "gridStepSize.max":{"type":float, "min":0.01, "max":1},
    "gridStepSize.step":{"type":float, "min":0.0001, "max":0.01},
    "simulationTime.value":float,
    "simulationTime.min":{"type":float, "min":0.01, "max":1},
    "simulationTime.max":{"type":float, "min":10, "max":1000},
    "simulationTime.step":{"type":float, "min":0.01, "max":1},
    "sourcePosition.value":float,
    "sourcePosition.step":{"type":float, "min":0.01, "max":1},
    "receiverPosition.value":float,
    "receiverPosition.step":{"type":float, "min":0.01, "max":1},
    "absCoeffL.value":float,
    "absCoeffL.step":{"type":float, "min":0.001, "max":0.1},
    "absCoeffR.value":float,
    "absCoeffR.step":{"type":float, "min":0.001, "max":0.1},
    "plotIthUpdate.value": int
    }

# Get some other elements
settingsDiv = initElement(id="settingsDiv")
plotDiv = initElement(id="plotDivId")
runButton = initElement(id="runButtonId")
pauseButton = initElement(id="pauseButtonId")
stopButton = initElement(id="stopButtonId")
downloadWavButton = initElement(id="downloadWavButtonId")

# Disable buttons that shouldn't be used until we're ready
runButton.disabled = True
pauseButton.disabled = True
stopButton.disabled = True
downloadWavButton.disabled = True

# Get some input elements and set some initial attribute values
gridDistance = initElement(id="gridDistanceId", min=0.1, max=10, step=0.1, value=gridLength, customPrintFormat="%0.1f",
    debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4)
gridStepSize = initElement(id="gridStepSizeId", min=0.001, max=0.1, step=0.001, value=0.01, customPrintFormat="%0.3f",
    debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4)
simulationTime = initElement(id="simulationTimeId", min=0.1, max=100, step=0.1, value=10, customPrintFormat="%0.1f",
    debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4)
sourcePosition = initElement(id="sourcePositionId", min=0, max=gridLength, step=0.01, value=0.25, customPrintFormat="%0.2f",
    debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4)
receiverPosition = initElement(id="receiverPositionId", min=0, max=gridLength, step=0.01, value=0.75, customPrintFormat="%0.2f",
    debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4)
absCoeffL = initElement(id="absCoeffLId", min=0, max=1.0, step=0.01, value=0.2, customPrintFormat="%0.2f",
    debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4)
absCoeffR = initElement(id="absCoeffRId", min=0, max=1.0, step=0.01, value=0.8, customPrintFormat="%0.2f",
    debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4)
plotIthUpdate = initElement(id="plotIthUpdateId", min=1, max=20, step=1, value=1, customPrintFormat="%i",
    debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4)

# Set parameters received from URL
# CAUTION: ALLOWS SETTING OF GLOBAL VARIABLES!!!!!!!!!!
setURLParams(URLParamsAllowed, varSpace=globals(), debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=1)

# Make sure any initial values are within min/max limits
constrainValue(gridDistance, doStep=True, doPrintFormat=True, debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4)
constrainValue(gridStepSize, doStep=True, doPrintFormat=True, debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4)
constrainValue(simulationTime, doStep=True, doPrintFormat=True, debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4)
sourcePosition.max = gridDistance.max   # Source can't be off the grid!
receiverPosition.max = gridDistance.max # Receiver can't be off the grid!
constrainValue(sourcePosition, doStep=True, doPrintFormat=True, debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4)
constrainValue(receiverPosition, doStep=True, doPrintFormat=True, debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4)
constrainValue(absCoeffL, doStep=True, doPrintFormat=True, debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4)
constrainValue(absCoeffR, doStep=True, doPrintFormat=True, debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4)
constrainValue(plotIthUpdate, doStep=True, doPrintFormat=True, debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4)

# Initialise FDTD object (and whether for it to use it's own internal debug printing)
fdtdDebugVerbosity = 3
fdtdDebug = int(DEBUG) >= fdtdDebugVerbosity
fdtd = pyFDTD(NDim=1, debug=fdtdDebug, debugPrefix=DEBUG_PREFIX+" (pyFDTD) : ")
fdtd.srcModel = "transparent 1D"    # Source model type
fdtd.betaMode = "constant"          # Only using betaBorder, so this is easiest option       
fdtd.betaType = "absorption"        # Mesh values interpreted as absorption coefficient
fdtd.doPlot = False                 # Don't do plotting within function (page does this separately here)
fdtd.doSrcRecCoordsCheck = False    # Don't check if source/receiver(s) are still on grid on setInputs (to stop them being deleted)
fdtd.saveRecData = True             # Do save receiver data ready for download
fdtd.recDataFile = io.BytesIO()     # Receiver data file gets saved to IO object
fdtd.saveGif = False                # Don't try and save a GIF (which think might not work for 1D anyway)

# Make Plotly objects...
# Define data object
plotlyData = plotly_go.Scatter(
    mode='lines',
    name='Simulation',
    line=dict(color='blue'))
# Define source object
plotlySrc = plotly_go.Scatter(
    mode='markers+text',
    marker=dict(size=16, color='rgba(100,100,255,0.25)', 
        line=dict(width=2, color='DarkSlateGrey')),
    x=[0],
    y=[0],
    text=["S#1"],
    textfont=dict(size=16),
    textposition='bottom right')
# Define receiver object
plotlyRec = plotly_go.Scatter(
    mode='markers+text',
    marker=dict(size=16, color='rgba(100,100,255,0.25)', 
        line=dict(width=2, color='DarkSlateGrey')),
    x=[0],
    y=[0],
    text=["R#1"],
    textfont=dict(size=16),
    textposition='bottom right')
# Define layout object
# (This can be quite complicated, but is very flexible)
plotlyLayout = plotly_go.Layout(
    xaxis=dict(
        title=dict(text='Distance (m)', font=dict(size=16)),
        tickfont=dict(size=16),
        showline=True, linewidth=2, linecolor="black", mirror=True, 
        showgrid=True, gridcolor="gray", gridwidth=1, griddash="dash",
        zeroline=True, zerolinecolor="gray", zerolinewidth=1,
        range=[0, gridDistance.value]),
    yaxis=dict(
        title=dict(text='Pressure', font=dict(size=16)),
        tickfont=dict(size=16),
        showline=True, linewidth=2, linecolor="black", mirror=True, 
        showgrid=True, gridcolor="gray", gridwidth=1, griddash="dash",
        zeroline=True, zerolinecolor="gray", zerolinewidth=1,
        range=[-2, 2]),
    margin=dict(l=90, b=90, r=30, t=30),
    hovermode='closest',
    plot_bgcolor="white",
    paper_bgcolor="white",
    autosize=True,
    showlegend=False)

# Trigger on run button click
@when("click", runButton)
async def runButtonClick(event):
    '''
    Run
    '''
    # Update to debug and screen
    eventId = event.target.id
    printToDebug("Click() "+eventId, DEBUG, DEBUG_PREFIX)
    printStatusUpdate("Run...")
    # If at start...
    if fdtd.loopNum == 0:
        # Get settings
        fdtdSettings()
    # Set button states
    runButton.disabled = True
    pauseButton.disabled = False
    stopButton.disabled = False
    downloadWavButton.disabled = True
    # Run simulation
    fdtd.running = True
    await runSimulation()

# Trigger on pause button click
@when("click", pauseButton)
def pauseButtonClick(event):
    '''
    Pause
    '''
    # Update to debug and screen
    eventId = event.target.id
    printToDebug("Click() "+eventId, DEBUG, DEBUG_PREFIX)
    printStatusUpdate("Pause")
    # Pause simulation
    fdtd.running = False
    # Set button states
    runButton.disabled = False
    pauseButton.disabled = True
    stopButton.disabled = False
    downloadWavButton.disabled = True

# Trigger on stop button click
@when("click", stopButton)
def stopButtonClick(event):
    '''
    Stop
    '''
    # Update to debug
    eventId = event.target.id
    printToDebug("Click() "+eventId, DEBUG, DEBUG_PREFIX)
    # Reset
    fdtdStop()
    # Update to screen that ready once everything has stopped 
    printStatusUpdate("Ready")

# Trigger on download wav button click
@when("click", downloadWavButton)
def downloadWavButtonClick(event):
    '''
    Download wav
    '''
    # Update to debug and screen
    eventId = event.target.id
    printToDebug("Click() "+eventId, DEBUG, DEBUG_PREFIX)
    printStatusUpdate("Download wav")
    # Download wav...
    # Print to debug
    printToDebug("Download triggered with filename = %s"%OP_FILENAME, DEBUG, DEBUG_PREFIX, verbosityLevel=2)
    # Trigger file download as an "audio/wav" type
    fileDownload(OP_FILENAME, fdtd.recDataFile, "audio/wav")
    # Status update
    printStatusUpdate("File download finished")

# Trigger on change to settings 
@when("change", settingsDiv)    # Note: this gets triggered when anything inside the settings div changes
def pageSettingsUpdate(event):
    '''
    Page settings update
    '''
    # Update to debug and screen
    eventId = event.target.id
    printToDebug("Click() "+eventId, DEBUG, DEBUG_PREFIX)
    # Specific case(s):
    if eventId == "gridDistanceId":
        # If size of grid changed...
        # Set max source/receiver position to same as grid length
        sourcePosition.max = gridDistance.value
        receiverPosition.max = gridDistance.value
        # Make sure values are within min/max limits
        constrainValue(sourcePosition, doStep=True, doPrintFormat=True, debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4)
        constrainValue(receiverPosition, doStep=True, doPrintFormat=True, debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4)
    # Update settings and replot when anything changes (AND simulation isn't running)
    if fdtd.loopNum == 0:
        fdtdSettings()
    # Constrain inputs
    constrainValue(event.target, doStep=True, doPrintFormat=True, debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4)

async def runSimulation():
    '''
    Run simulation
    '''
    # Print to debug
    printToDebug("Run simulation loop", DEBUG, DEBUG_PREFIX, verbosityLevel=2)
    # Run loop and plot
    while fdtd.running:
        # Update plot on this loop?
        validStep = fdtd.runStep()
        doPlot = not (fdtd.loopNum % fdtd.plotIthUpdate)
        if doPlot:
            # update plot
            updatePlot(y=fdtd.p)
            # Pause to allow plotting to happen
            await asyncio.sleep(plotPauseTime)
            # TODO Status update for run time????
    # Any tidying up if at end
    if fdtd.loopNum >= fdtd.Nt-1:
        finishedSimulation()

def finishedSimulation():
    '''
    Tidy up on end of simulation
    '''
    # Print to debug
    printToDebug("Finished simulation", DEBUG, DEBUG_PREFIX, verbosityLevel=2)
    # Stopped
    fdtd.stop() # Basically just means fdtd.running = False
    # Set button states
    runButton.disabled = False
    pauseButton.disabled = True
    stopButton.disabled = True
    downloadWavButton.disabled = False
    # Reset simulation (ready for if run is pressed again)
    fdtd.runReset()

def fdtdSettings():
    '''
    set FDTD model settings
    '''
    # Print to debug
    printToDebug("Settings update", DEBUG, DEBUG_PREFIX, verbosityLevel=2)
    # Grid size/resolution
    D = float(gridDistance.value)
    dx = float(gridStepSize.value)
    N = int(round(D/dx)+1)
    dx = D/(N-1)    # Actual dx may be slightly different to requested
    # FDTD grid settings
    fdtd.X = dx                                         # Grid spacing
    fdtd.t = float(simulationTime.value)*1e-3           # Simulation time (s -> ms)
    # Set inputs
    fdtd.setInputs()
    # Make new empty mesh
    fdtd.newEmptyMesh([N])
    # Add absorption coefficients of end surfaces
    fdtd.betaBorder = [float(absCoeffL.value), float(absCoeffR.value)]
    # Update (first) source
    xSrc = [float(sourcePosition.value)]
    fdtd.editSrc(xyz=xSrc, i=0)
    # Update (first) receiver
    xRec = [float(receiverPosition.value)]
    fdtd.editRec(xyz=xRec, i=0)
    # In case anything edited by user means we have more than one source and/or receiver
    xSrc = []
    for x in fdtd.srcXyz: xSrc += x
    xRec = []
    for x in fdtd.recXyz: xRec += x
    # Plot interval setting
    fdtd.plotIthUpdate = int(plotIthUpdate.value)
    # Reset simulation 
    fdtd.runReset()
    # Prepare mesh
    fdtd.prepareMesh()
    # x plot data and range
    x = dx*np.arange(N)
    xRange = [0, D]
    # Update plot
    updatePlot(x=x, y=fdtd.p, xSrc=xSrc, xRec=xRec, xRange=xRange)

def fdtdStop():
    '''
    FDTD stop and replot
    '''
    # Print to debug
    printToDebug("FDTD stop", DEBUG, DEBUG_PREFIX, verbosityLevel=2)
    # Reset simulation and button states
    finishedSimulation()
    # Don't allow download on stop (need to finish properly to have downloadable result)
    downloadWavButton.disabled = True
    # Reset plot with current settings
    fdtdSettings()

def updatePlot(x=None, y=None, xSrc=None, xRec=None, xRange=None, yRange=None):
    '''
    Update plot
    '''
    # Print to debug
    printToDebug("Plot update", DEBUG, DEBUG_PREFIX, verbosityLevel=2)
    # Make Plotly plot using Plotly for Python (see: https://plotly.com/python/)...
    # Update data
    if not x is None:       plotlyData['x'] = x
    if not y is None:       plotlyData['y'] = y
    # Update layout
    if not xRange is None:  plotlyLayout['xaxis_range'] = xRange
    if not yRange is None:  plotlyLayout['yaxis_range'] = yRange
    # Update to source/receiver position(s) and text labels
    if not xSrc is None:
        plotlySrc['x'] = xSrc
        txt = []
        for i in range(len(xSrc)): txt.append("S#%i"%(i+1))
        plotlySrc['text'] = txt
    if not xRec is None:
        plotlyRec['x'] = xRec
        txt = []
        for i in range(len(xRec)): txt.append("R#%i"%(i+1))
        plotlyRec['text'] = txt
    # Make figure
    fig = plotly_go.Figure(data=[plotlyData, plotlySrc, plotlyRec], layout=plotlyLayout)
    # Convert to JSON format and add to page using Plotly.js
    # (See header info in index file for ensuring we have this)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    # Make/update plot
    window.Plotly.react(plotDiv.id, window.JSON.parse(graphJSON))

# Trigger stop button click, which resets everything to a starting state
sendEvent(stopButton, "click", debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=2)
# Then run settings, which plots using 
fdtdSettings()

# Let know we're at the end of the code
# Note: verbosityLevel=0 means print even if debug messages turned off
printToDebug("End of PyScript code", DEBUG, DEBUG_PREFIX, verbosityLevel=0)

# Send custom event (with name being listened for to close splash screen)
# Note we could just do this manually - e.g. document.getElementById('loadingDiv').close() - but this is more satisfying!
sendCustomEvent("py:loaded", debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=3)

