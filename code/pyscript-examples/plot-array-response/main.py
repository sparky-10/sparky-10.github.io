from pyscript import when, document, display, window
import numpy as np
from ps_tools import printToDebug, initElement, setURLParams, sendCustomEvent, sendEvent
from ps_tools import constrainInputValue as constrainValue
from myPyFunc import myPyFunc
import matplotlib.pyplot as plt
import plotly.graph_objs as plotly_go
import plotly.utils
import json

# Some basic settings
DEBUG = False                   # If printing to debug console (use integers to for verbosity level
DEBUG_PREFIX = "PY"             # Prefix for identifying messages in debug console
STATUS_PREFIX = "Status: "      # Prefix for on screen status update
freq = 1000                     # Frequency (Hz)
frequencyMin = 50               # Min allowed frequency (Hz)
frequencyStep = 10              # Frequency step size (Hz)
nFrequencyDecades = 2           # Number of decades in settable frequency range
rangedB = 45                    # Range in dB for y-axis of plot(s)

# Max frequency allowed (Hz)
frequencyMax = frequencyMin*10**nFrequencyDecades

# URL settable parameters that we allow, and their data types/limits for setting
# E.g. append URL with ?numSource.value=12&frequency.value=4000
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
    }

# Set parameters received from URL - Do DEBUG separately first so if any change this affects everything that follows
# CAUTION: ALLOWS SETTING OF GLOBAL VARIABLES!!!!!!!!!!
setURLParams({"DEBUG":int}, varSpace=globals(), debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=0)

# Print status update to screen
statusUpdate = initElement(id="statusUpdateId")
def printStatusUpdate(txt):
    statusUpdate.innerText = STATUS_PREFIX + txt

# Initial status
printStatusUpdate("Loading...")

# Get some input elements and set some initial attribute values
# (effectively overriding what is in index file)
numSource = initElement(id="numSourceId", min=1, max=20, step=1, value=10, customPrintFormat="%i",
    debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4) 
dxSource = initElement(id="dxSourceId", min=0.01, max=1, step=0.01, value=0.5, customPrintFormat="%0.2f",
    debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4)
frequency = initElement(id="frequencyId", min=frequencyMin, max=frequencyMax, step=frequencyStep, value=freq, customPrintFormat="%0.1f",
    debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4)
frequencySlider = initElement(id="frequencySliderId", min=0, max=nFrequencyDecades, step=0.001, value=np.log10(freq/frequencyMin),
    debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4)
plotMethod = initElement(id="plotMethodId", selectedIndex=0, 
    debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4)

# Get some other elements
settingsDiv = initElement(id="settingsDiv")
plotDivs = [initElement(id="plotlyDivId"),
    initElement(id="mplReplaceDivId"),
    initElement(id="mplUpdateDivId")]

# Set parameters received from URL
# CAUTION: ALLOWS SETTING OF GLOBAL VARIABLES!!!!!!!!!!
setURLParams(URLParamsAllowed, varSpace=globals(), debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=1)

# Make amplitude reset button (not on page yet)
amplitudeResetButton = initElement(nodeName="button", id="amplitudeResetButtonId",
    title="Reset amplitudes", name="source-amplitude-reset", textContent="Reset all",
    style="width:30%; float:right;",
    debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4)

# Make amplitude elements and their labels (not on page yet)
numAmplitude = int(numSource.max)
amplitude = [None]*numAmplitude
amplitudeLabel = [None]*numAmplitude
for i in range(numAmplitude):
    amplitude[i] = initElement(id="amplitude%02iId"%i, type="number", value=1, min=-1, max=1, step=0.01,
        title="Source #%i amplitude"%i, name="source-amplitude-%i"%i, autocomplete="off", 
        style="width:25%; float:right;", customPrintFormat="%0.2f",
        debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=4)
    amplitudeLabel[i] = initElement(**{"nodeName":"label", "id":"amplitudeLabel%02iId"%i, 
        "innerHTML":"A<sub>%i</sub>"%i, "for":amplitude[i].id,
        "style":"width:70%; float:left;",
        "debug":DEBUG, "debugPrefix":DEBUG_PREFIX, "verbosityLevel":4}) # $
# $ Note "**" used to pass as dict which allows passing of e.g. "for" which is a Python reserved term

# Add amplitude button and number inputs to page
settingsDiv.appendChild(amplitudeResetButton)
settingsDiv.appendChild(document.createElement("br"))
settingsDiv.appendChild(document.createElement("br"))
# Add amplitude elements to page
for i, amp in enumerate(amplitude):
    # Add labels and number boxes to page
    settingsDiv.appendChild(amplitudeLabel[i])
    settingsDiv.appendChild(amp)
    # Add break (next line)
    if i <= numAmplitude-1: settingsDiv.appendChild(document.createElement("br"))

# Make sure any initial values are within min/max limits
constrainValue(numSource, doStep=True, doPrintFormat=True, debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=5)
constrainValue(dxSource, doStep=True, doPrintFormat=True, debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=5)
constrainValue(frequency, doStep=False, doPrintFormat=True, debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=5)
constrainValue(frequencySlider, doStep=False, doPrintFormat=False, debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=5)
for amp in amplitude:
    constrainValue(amp, doStep=True, doPrintFormat=True, debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=5)

# Initialise directivity object
myPyFuncObj = myPyFunc(debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=2)

# Make Matplotlib "update" object
mplUpdateFig, mplUpdateAx = plt.subplots()
mplUpdateAx.set_xlabel("Angle (degrees)") 
mplUpdateAx.set_ylabel("Level (dB)")
mplUpdateAx.set_title("Array directivity")
mplUpdateAx.grid()

# Make Plotly objects (see: https://plotly.com/python/)...
# Define data object
plotlyData = plotly_go.Scatter(
    mode='lines',
    name='Directivity',
    line=dict(color='blue'))
# Define layout object
# (This can be quite complicated, but is very flexible)
plotlyLayout = plotly_go.Layout(
    title=dict(text='Array directivity', font=dict(size=18),
        y=0.9, x=0.5, xanchor='center', yanchor='top'),
    xaxis=dict(
        title=dict(text='Angle (degrees)', font=dict(size=16)),
        tickfont=dict(size=14),
        showline=True, linewidth=2, linecolor="black", mirror=True, 
        showgrid=True, gridcolor="gray", gridwidth=1, griddash="dash",
        zeroline=True, zerolinecolor="gray", zerolinewidth=1),
    yaxis=dict(
        title=dict(text='Level (dB)', font=dict(size=16)),
        tickfont=dict(size=14),
        showline=True, linewidth=2, linecolor="black", mirror=True, 
        showgrid=True, gridcolor="gray", gridwidth=1, griddash="dash",
        zeroline=True, zerolinecolor="gray", zerolinewidth=1),
    hovermode='closest',
    plot_bgcolor="white",
    paper_bgcolor="white",
    autosize=True)

# Trigger on any plot method change
@when("change", plotMethod)
def plotMethodChange(event):
    '''
    Apply appropriate changes on plot type change:
    - Directivity calculation and resulting plot 
    '''
    # Update to debug
    eventId = event.target.id
    printToDebug("Change to "+eventId, DEBUG, DEBUG_PREFIX)
    printToDebug("ID: %s - value = %s"%(eventId, event.target.options[event.target.selectedIndex].text), DEBUG, DEBUG_PREFIX, verbosityLevel=2)
    # Update directivity (which updates plot)
    updateDirectivity()

# Trigger on any number of source change
# Note: on "input" means straight away, not just when change is accepted
# The down side of this is it interferes with user typed entries - e.g. a single entered value triggers an update
# This means longer user typed values will not work well  
@when("input", numSource)  
def numSourceChange(event):
    '''
    Apply appropriate changes on number of source change:
    - Ensure value is valid
    - Number of source amplitude boxes shown
    - Directivity calculation and resulting plot 
    '''
    # Update to debug
    eventId = event.target.id
    printToDebug("Change to "+eventId, DEBUG, DEBUG_PREFIX)
    # Make sure any entered value is within min/max limits
    constrainValue(event, doStep=True, doPrintFormat=True, debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=5)
    printToDebug("ID: %s - value = %s"%(eventId, event.target.value), DEBUG, DEBUG_PREFIX, verbosityLevel=2)
    # Update displaying of amplitude elements
    amplitudeDisplayChange()
    # Update directivity
    updateDirectivity()

# Trigger on any source spacing or amplitude element change
@when("input", dxSource)    # Stack triggers...
@when("input", amplitude)   # Note this works even for lists of elements like this
def numericInputChange(event):
    '''
    Apply appropriate changes on input:
    - Ensure value is valid
    - Directivity calculation and resulting plot 
    '''
    # Update to debug
    eventId = event.target.id
    printToDebug("Change to "+eventId, DEBUG, DEBUG_PREFIX)
    # Make sure any entered value is within min/max limits
    constrainValue(event, doStep=True, doPrintFormat=True, debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=5)
    printToDebug("ID: %s - value = %s"%(eventId, event.target.value), DEBUG, DEBUG_PREFIX, verbosityLevel=2)
    # Update directivity
    updateDirectivity()

# We use these to keep number box and slider in sync
def updateFrequencySlider():
    # Update frequency slider to match frequency number box...
    frequencySlider.value = np.log10(float(frequency.value)/float(frequency.min))
    constrainValue(frequencySlider, doStep=False, doPrintFormat=False, debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=5)
def updateFrequencyNumberBox():
    # Update frequency number box to match frequency slider...
    frequency.value = float(frequency.min)*10**float(frequencySlider.value)
    constrainValue(frequency, doStep=False, doPrintFormat=True, debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=5)

# Trigger on any frequency element change
@when("input", frequency)
def frequencyChange(event):
    '''
    Apply appropriate changes on frequency number box change:
    - Ensure value is valid
    - Make sure in sync with slider
    - Directivity calculation and resulting plot 
    '''
    # Print to debug
    eventId = event.target.id
    printToDebug("Change to "+eventId, DEBUG, DEBUG_PREFIX)
    # Make sure any entered value is within min/max limits
    constrainValue(event, doStep = False, doPrintFormat=True, debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=5)
    printToDebug("ID: %s - value = %s"%(eventId, event.target.value), DEBUG, DEBUG_PREFIX, verbosityLevel=2)
    # Update slider
    updateFrequencySlider()
    # Update directivity
    updateDirectivity()

# Trigger on any frequency slider element input
@when("input", frequencySlider)    # Note: input means changes as slider moves, not just when mouse click is released
def frequencySliderChange(event):
    '''
    Apply appropriate changes on frequency slider change:
    - Ensure value is valid
    - Make sure in sync with number box
    - Directivity calculation and resulting plot 
    '''
    # Print to debug
    eventId = event.target.id
    printToDebug("Change to "+eventId, DEBUG, DEBUG_PREFIX)
    # Make sure any entered value is within min/max limits
    constrainValue(event, doStep=False, doPrintFormat=False, debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=5)
    printToDebug("ID: %s - value = %s"%(eventId, event.target.value), DEBUG, DEBUG_PREFIX, verbosityLevel=2)
    # Update number box
    updateFrequencyNumberBox()
    # Update directivity
    updateDirectivity()

# Trigger on amplitude reset button click
@when("click", amplitudeResetButton)
def amplitudeReset(event):
    '''
    Reset amplitudes and update directivity/plot
    '''
    # Print to debug
    eventId = event.target.id
    printToDebug("Change to "+eventId, DEBUG, DEBUG_PREFIX)
    # Set all amplitudes to 1.0
    for amp in amplitude:
        amp.value = "1.0"
    # Update directivity
    updateDirectivity()

def amplitudeDisplayChange():
    '''
    Update displaying of amplitudes
    I.e. change visible/hidden state of amplitude number boxes (and labels)
    '''
    # Print to debug
    printToDebug("Amplitude display change", DEBUG, DEBUG_PREFIX, verbosityLevel=2)
    # Hide/disable unused amplitude elements (and labels)
    nSource = int(numSource.value)
    for i, amp in enumerate(amplitude):
        # Note - Don't really need disabled if using visible as well, but just for completeness/example
        if i >= nSource:
            amp.disabled = "disabled"
            amp.style.visibility = 'hidden'
            amplitudeLabel[i].style.visibility = "hidden"
        else:
            amp.removeAttribute("disabled")
            amp.style.visibility = "visible"
            amplitudeLabel[i].style.visibility = "visible"

def updatePlot(x, y, xRange, yRange):
    '''
    # Update the plot(s)
    '''
    # Print to debug
    printToDebug("Plot update", DEBUG, DEBUG_PREFIX)
    # Plot according to selected type
    plotOption = int(plotMethod.selectedIndex)
    plotType = plotMethod.options[plotOption].text
    # Update to debug and screen
    printToDebug("Plot = "+plotType, DEBUG, DEBUG_PREFIX, verbosityLevel=2)
    printStatusUpdate("Plotting using "+plotType)
    # Hide all plots
    # Note: use display rather than visibility to stop hidden divs taking up space on screen
    for div in plotDivs:
        div.style.display = "none"
    # Then make relevant plot visible
    plotDiv = plotDivs[plotOption]
    plotDiv.style.display = ""
    # Make/update plot according to type
    match plotOption:
        case 0:
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
            # Make/update plot (use of 'react' is supposed to be more responsive/efficient)
            window.Plotly.react(plotDiv.id, window.JSON.parse(graphJSON))
        case 1:
            # Make new plot
            fig, ax = plt.subplots()
            ax.plot(x, y, 'b-', linewidth=1, label='Directivity')
            ax.set_xlabel("Angle (degrees)") 
            ax.set_ylabel("Level (dB)")
            ax.set_title("Array directivity")
            ax.set_xlim(xRange)
            ax.set_ylim(yRange)
            ax.grid()
            # Add to page
            display(fig, target=plotDiv.id, append=False)
            # Close fig after displaying
            plt.close(fig)
        case 2:
            # Update plot...
            if not len(mplUpdateAx.lines):
                # Plot if no plotted data yet
                mplUpdateAx.plot(x, y, 'b-', linewidth=1, label='Directivity')
                mplUpdateAx.set_xlim(xRange)
            else:
                # Otherwise update plot data if plotted line already exists
                mplUpdateAx.lines[0].set_ydata(y)
            # Set y range
            mplUpdateAx.set_ylim(yRange)
            # Add to page
            display(mplUpdateFig, target=plotDiv.id, append=False)

# Update the directivity
def updateDirectivity():
    '''
    Update directivity calculation and plot
    '''
    # Print to debug
    printToDebug("Update directivity", DEBUG, DEBUG_PREFIX)
    # Get settings from page
    N = int(numSource.value)
    dx = float(dxSource.value)
    f = float(frequency.value)
    A = np.zeros(N)
    for i in range(N):
        A[i] = float(amplitude[i].value)
    # Update directivity in function
    myPyFuncObj.updateDirectivity(A=A, dx=dx, f=f)
    # Directivity in dB
    PdB = 20.0*np.log10(np.abs(myPyFuncObj.p))
    # Max y range value for plotting 
    maxPdB = 20.0*np.log10(float(numSource.value)) + 2.5
    # Update plot
    updatePlot(myPyFuncObj.theta, PdB, 
        [min(myPyFuncObj.theta), max(myPyFuncObj.theta)], 
        [maxPdB-rangedB , maxPdB])

# Update number of amplitudes on display
# (Do at start so we have the right number shown)
amplitudeDisplayChange()

# Update slider by triggering frequency input
# (Because we allow frequency to be potentially changed via URL, and we want slider to be in sync)
sendEvent(frequency, "input", debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=3)

# Run making of plot so have plot at the start
updateDirectivity()

# Print to debug (let know we're at the end of the code)
# Note: verbosityLevel=0 means print even if debug messages turned off
printToDebug("End of PyScript code", DEBUG, DEBUG_PREFIX, verbosityLevel=0)

# Send custom event (with name being listened for to close splash screen)
# Note we could just do this manually - e.g. document.getElementById('loadingDiv').close() - but this is more satisfying!
sendCustomEvent("py:loaded", debug=DEBUG, debugPrefix=DEBUG_PREFIX, verbosityLevel=3)


