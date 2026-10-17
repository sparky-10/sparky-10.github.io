from pyscript import when, document, window
import numpy as np
from ps_tools import printToDebug, initElement, setURLParams, sendCustomEvent
from ps_tools import sendEvent # TODO Still need this??? 
from ps_tools import constrainInputValue as constrainValue
import plotly.graph_objs as plotly_go
import plotly.utils
import json
from pyFDTD import pyFDTD

# Some basic settings
DEBUG = False                   # If printing to debug console (use integers to for verbosity level
DEBUG_PREFIX = "PY"             # Prefix for identifying messages in debug console
STATUS_PREFIX = "Status: "      # Prefix for on screen status update

#TODO Set extra initial variables
'''freq = 1000                     # Frequency (Hz)
frequencyMin = 50               # Min allowed frequency (Hz)
frequencyStep = 10              # Frequency step size (Hz)
nFrequencyDecades = 2           # Number of decades in settable frequency range
rangedB = 45                    # Range in dB for y-axis of plot(s)

# Max frequency allowed (Hz)
frequencyMax = frequencyMin*10**nFrequencyDecades'''

# Set parameters received from URL - Do DEBUG first separately so affects everything else that follows
# CAUTION: ALLOWS SETTING OF GLOBAL VARIABLES!!!!!!!!!!
setURLParams({"DEBUG":int}, varSpace=globals(), debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=0)

# Print status update to screen
statusUpdate = initElement(id="statusUpdateId")
def printStatusUpdate(txt):
    statusUpdate.innerText = STATUS_PREFIX + txt

# Initial status
printStatusUpdate("Loading...")

# TODO 
# URL settable parameters that we allow, and their data types/limits for setting
URLParamsAllowed = {}
'''# E.g. append URL with ?numSource.value=12&frequency.value=4000
URLParamsAllowed = {
    "plotMethod.selectedIndex":{"type":int, "min":0, "max":2},
    "numSource.value":int, 
    "numSource.min":{"type":int, "min":1, "max":50},
    "numSource.max":{"type":int, "min":1, "max":50},
    "dxSource.value":float,
    "dxSource.min":{"type":float, "min":0.001, "max":10},
    "dxSource.max":{"type":float, "min":0.001, "max":10},
    "dxSource.step":{"type":float, "min":0.001, "max":0.1},
    "frequency.value":float, 
    "frequency.min":{"type":float, "min":10, "max":20000},
    "frequency.max":{"type":float, "min":10, "max":20000}
    }'''

# Get some other elements
settingsDiv = initElement(id="settingsDiv")
plotlyDiv = initElement(id="plotlyDivId")
runButton = initElement(id="runButtonId")
pauseButton = initElement(id="pauseButtonId")
stopButton = initElement(id="stopButtonId")

# Disable buttons that shouldn't be used until we have a result
runButton.disabled = False
pauseButton.disabled = True
stopButton.disabled = True

# TODO
# Get some input elements and set some initial attribute values
'''numSource = initElement(id="numSourceId", min=1, max=20, step=1, value=10, customPrintFormat="%i",
    debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4) 
dxSource = initElement(id="dxSourceId", min=0.01, max=1, step=0.01, value=0.5, customPrintFormat="%0.2f",
    debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4)
frequency = initElement(id="frequencyId", min=frequencyMin, max=frequencyMax, step=frequencyStep, value=freq, customPrintFormat="%0.1f",
    debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4)
frequencySlider = initElement(id="frequencySliderId", min=0, max=nFrequencyDecades, step=0.001, value=np.log10(freq/frequencyMin),
    debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4)
plotMethod = initElement(id="plotMethodId", selectedIndex=0, 
    debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4)'''

# Set parameters received from URL
# CAUTION: ALLOWS SETTING OF GLOBAL VARIABLES!!!!!!!!!!
setURLParams(URLParamsAllowed, varSpace=globals(), debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=1)

# TODO
# Make sure any initial values are within min/max limits
'''
constrainValue(numSource, doStep=True, doPrintFormat=True, debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=5)
constrainValue(dxSource, doStep=True, doPrintFormat=True, debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=5)
constrainValue(frequency, doStep=False, doPrintFormat=True, debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=5)
constrainValue(frequencySlider, doStep=False, doPrintFormat=False, debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=5)
for amp in amplitude:
    constrainValue(amp, doStep=True, doPrintFormat=True, debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=5)'''

# Initialise FDTD object for
fdtdDebugVerbosity = 2
fdtdDebug = int(DEBUG) >= fdtdDebugVerbosity
fdtd = pyFDTD(NDim=1, debug=fdtdDebug)

# FDTD settings
fdtd.t = 10e-3
fdtd.X = 10e-3
fdtd.setInputs()
fdtd.plotIthUpdate = 5
fdtd.doPlot = False
fdtd.saveRecData = False
fdtd.saveGif = False
fdtd.betaMode = 'varying'
fdtd.mesh[0:10] = 1
fdtd.mesh[90:] = 0.5



# Make Plotly objects...
# Define data object
# TODO Disable some user controls???
plotlyData = plotly_go.Scatter(
    mode='lines',
    name='Simulation',
    line=dict(color='blue'))
# Define layout object
# (This can be quite complicated, but is very flexible)
plotlyLayout = plotly_go.Layout(
    title=dict(text='FDTD simulation', font=dict(size=18),
        y=0.9, x=0.5, xanchor='center', yanchor='top'),
    xaxis=dict(
        title=dict(text='Time (s)', font=dict(size=16)),
        tickfont=dict(size=14),
        showline=True, linewidth=2, linecolor="black", mirror=True, 
        showgrid=True, gridcolor="gray", gridwidth=1, griddash="dash",
        zeroline=True, zerolinecolor="gray", zerolinewidth=1),
    yaxis=dict(
        title=dict(text='Pressure', font=dict(size=16)),
        tickfont=dict(size=14),
        showline=True, linewidth=2, linecolor="black", mirror=True, 
        showgrid=True, gridcolor="gray", gridwidth=1, griddash="dash",
        zeroline=True, zerolinecolor="gray", zerolinewidth=1),
    hovermode='closest',
    plot_bgcolor="white",
    paper_bgcolor="white",
    autosize=True)

# Trigger on run button click
@when("click", runButton)
def runButtonClick(event):
    # Update to debug
    eventId = event.target.id
    printToDebug("Click() "+eventId, DEBUG, DEBUG_PREFIX)
    printStatusUpdate("Run")
    #printToDebug("ID: %s - value = %s"%(eventId, event.target.options[event.target.selectedIndex].text), DEBUG, DEBUG_PREFIX, verbosityLevel=2)
    # Run simulation
    fdtd.run()

# Trigger on pause button click
@when("click", pauseButton)
def pauseButtonClick(event):
    # Update to debug
    eventId = event.target.id
    printToDebug("Click() "+eventId, DEBUG, DEBUG_PREFIX)
    printStatusUpdate("Pause")
    # Pause simulation

# Trigger on stop button click
@when("click", stopButton)
def stopButtonClick(event):
    # Update to debug
    eventId = event.target.id
    printToDebug("Click() "+eventId, DEBUG, DEBUG_PREFIX)
    printStatusUpdate("Stop")
    # Stop simulation

# Update the plot(s)
def updatePlot(x, y, xRange, yRange):
    # Print to debug
    printToDebug("Plot update", DEBUG, DEBUG_PREFIX, verbosityLevel=4)
    # Make Plotly plot using Plotly for Python (see: https://plotly.com/python/)...
    # Update data
    plotlyData['x'] = x
    plotlyData['y'] = y
    # Update layout
    plotlyLayout['xaxis_range'] = xRange
    plotlyLayout['yaxis_range'] = yRange
    # Make figure
    fig = plotly_go.Figure(data=[plotlyData], layout=plotlyLayout)
    # Convert to JSON format and add to page using Plotly.js
    # (See header info in index file for ensuring we have this)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    # Make/update plot
    window.Plotly.react(plotDiv.id, window.JSON.parse(graphJSON))

# Let know we're at the end of the code
# Note: verbosityLevel=0 means print even if debug messages turned off
printToDebug("End of PyScript code", DEBUG, DEBUG_PREFIX, verbosityLevel=0)

# Send custom event (with name being listened for to close splash screen)
# Note we could just do this manually - e.g. document.getElementById('loadingDiv').close() - but this is more satisfying!
sendCustomEvent("py:loaded", debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=3)


