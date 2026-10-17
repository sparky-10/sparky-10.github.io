from pyscript import window, document, fetch, ffi, util
import js
import numpy as np
import inspect

'''
Set of utility functions for use with PyScript
(Plus some other random functions)
'''

def printToDebug(txt, debug=False, debugPrefix="", verbosityLevel=1):
    '''
    Print a debug message to console
    '''
    # Convert to int for use with verbosity level 
    debug = int(debug)
    # Print debug message (if we're being this verbose!)
    if debug >= verbosityLevel:
        if not debugPrefix is None:
            debugText = debugPrefix
            if len(debugText) > 0:
                debugText += " : "
        else:
            debugText = ""
        debugText += str(txt)
        # Print to console/terminal
        print(debugText)

def editDebugPrefix(debugOptions):
    '''
    Append calling function to debugPrefix if there is one
    '''
    if "debugPrefix" in debugOptions:
        # Get calling function, file etc..
        prevFrame = inspect.currentframe().f_back
        (filename, lineNumber, functionName, lines, index) = inspect.getframeinfo(prevFrame)
        filename = filename.split('/')[-1].split('.')[0]
        # Add details to prefix
        debugAppend = " (%s.%s)"%(filename, functionName)
        debugOptions["debugPrefix"] += debugAppend
    return debugOptions
    
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

def fileDownload(filename, ioObj, blobType, **debugOptions):
    """
    Trigger browser download of file content
    See https://docs.pyscript.net/2026.7.3/faq/#loading-files
    """
    # For debug
    debugOptions = editDebugPrefix(debugOptions)
    # Convert to JS
    buf = ioObj
    buf.seek(0)
    content = ffi.to_js(buf.read())
    # Ensure use the correct mime-type!
    blob = window.Blob.new([content], ffi.to_js({"type": blobType}))
    # Create a temporary download link/URL.
    url = window.URL.createObjectURL(blob)
    link = window.document.createElement("a")
    link.href = url
    link.download = filename
    # Print to debug
    printToDebug("Trigger download file = "+str(filename), **debugOptions)
    # Activate the link (pretend to click it)
    link.click()
    # Then revoke the temporary URL
    window.URL.revokeObjectURL(url)

def constrain(v, vMin=None, vMax=None, vStep=None, **debugOptions):
    '''
    Constrain value
    '''
    # For debug
    debugOptions = editDebugPrefix(debugOptions)
    debugStr = "Constrain value "+str(v)+" -> "
    # Make sure increment of step size if requested
    if not vStep is None:
        if not vMin is None: v = v-vMin
        v = vStep*round(v/vStep)
        if not vMin is None: v = v+vMin
    # Restrict to within min/max range (i.e. like numpy.clip)
    if not vMin is None: v = max(v,vMin)
    if not vMax is None: v = min(v,vMax)
    # Print to debug
    debugStr += str(v)
    printToDebug(debugStr, **debugOptions)
    # Return constrained value
    return v

def constrainInputValue(ip, doStep = False, doPrintFormat=False, **debugOptions):
    '''
    Constrain value of HTML input element
    Includes potential checking for "customPrintFormat" attribute which allows specifying of number to string formatting
    '''
    # For debug
    debugOptions = editDebugPrefix(debugOptions)
    # If it's an event object, get the target
    if hasattr(ip, "target"):
        ip = ip.target
    # Print to debug
    debugStr = "Constrain value "
    if hasattr(ip, "id"):
        debugStr += str(ip.id)+" "
    debugStr += str(ip.value)+" -> "
    # Get value, step, min, and max values
    v = float(ip.value)
    vStep = ip.step
    vMin = ip.min
    vMax = ip.max
    # Make floats
    if vStep == "": vStep = None
    else: vStep = float(vStep)
    if vMin == "": vMin = None
    else: vMin = float(vMin)
    if vMax == "": vMax = None
    else: vMax = float(vMax)
    # No step size if not doing steps
    if not doStep: vStep = None
    # Constrain value
    v = constrain(v, vMin, vMax, vStep)
    # Final output
    if doPrintFormat:
        if isinstance(doPrintFormat, str):
            # Assume been passed string specifying how to format
            printFormat = doPrintFormat
        elif hasattr(ip, "customPrintFormat"):
            # Check for format in element (custom attribute)
            printFormat = ip.customPrintFormat
        else:
            # Decimal places assumed for writing back to string
            # (if no alternative formatting given)
            decPlaces = 0   # Min decimal places used for auto formatting
            if not vMin is None or vMin == 0: 
                decPlaces = max(decPlaces, int(np.ceil(np.log10(1/np.abs(vMin)))))
            if not vStep is None or vStep == 0:
                decPlaces = max(decPlaces, int(np.ceil(np.log10(1/vStep))))
            # Use automated decimal places for formatting
            printFormat = "%"+("0.%i"%decPlaces)+"f"
        # Try to format as string
        if isinstance(printFormat, str) and not printFormat == "":
            ip.value = printFormat%v
        else:
            # No formatting
            ip.value = v
    else:
        # No formatting
        ip.value = v
    # Print to debug
    debugStr += str(v)
    printToDebug(debugStr, **debugOptions)

def initElement(**elementArgs):
    '''
    Update and/or create an HTML element
    Note usual warnings about security apply - use of e.g. innerHTML is not advised
    '''
    # For debug
    # (remove debug arguments from function  input,
    # due to arguments coming in in one big dict, and being a bit of mash of 
    # HTML element attributes and debug flags)
    debugOptions = {}
    if "debug" in elementArgs: debugOptions["debug"] = elementArgs.pop("debug")
    if "debugPrefix" in elementArgs: debugOptions["debugPrefix"] = elementArgs.pop("debugPrefix")
    if "verbosityLevel" in elementArgs: debugOptions["verbosityLevel"] = elementArgs.pop("verbosityLevel")
    debugOptions = editDebugPrefix(debugOptions)
    # Default element type
    defaultElementType = "input"    
    # Try to get element from document if passed an id
    if "id" in elementArgs:
        # Get element from document
        el = document.getElementById(elementArgs["id"])
        # Convert if get a JsNull (i.e. if couldn't find)
        if ffi.is_none(el): el = None
        # If element found, remove id as don't want to re set this below
        if not el is None: elementArgs.pop("id")
    else:
        el = None
    # Get element nodeName (for if making) and remove to stop any future attempt to set
    if "nodeName" in elementArgs:
        nodeName = elementArgs.pop("nodeName")
    else:
        nodeName = defaultElementType
    # If not got an element, make a new one
    if el is None:
        # Create new element
        el = document.createElement(nodeName)
    # Move 'value' to end if exists
    # (Due to odd behaviour sometimes where e.g. setting min after value alters value)
    if "value" in elementArgs:
        elementArgs["value"] = elementArgs.pop("value")
    # If we have a valid element...
    # Note: the below is slightly messy, but HTML property vs attribute setting is inherently messy!!
    if not el is None:
        # Set all attributes/properties remaining in input arguments
        # (Note: this will attempt to add anything passed, including...
        # 'custom' user defined ones!!!!
        # Sometimes advised against attributes (e.g. innerHTML)
        for key in elementArgs.keys():
            try:
                # Try to set the property...
                # This could fail if key is an attribute, not a property
                setattr(el, key, str(elementArgs[key]))
            except:
                # Try to set using setAttribute
                el.setAttribute(key, elementArgs[key])
            # Print to debug
            printToDebug("Element setting - %s = %s"%(key, elementArgs[key]), **debugOptions)
    return el
    
def getURLParams(searchKeys, **debugOptions):
    '''
    Get value(s) for search key(s) from URL (if exists) 
    '''
    # For debug
    debugOptions = editDebugPrefix(debugOptions)
    # Get any URL appended text
    queryString = window.location.search
    # Get any URL parameters
    urlParams = util.js.URLSearchParams.new(queryString)
    # Internal function used to get key value
    def getParam(key):
        if urlParams.has(key): return urlParams.get(key)
        else: return None
    # If search key(s) exists, return value
    # Do as either list/dict or assume single key
    if isinstance(searchKeys, list) or isinstance(searchKeys, dict):
        outputValues = [None]*len(searchKeys)
        for i, key in enumerate(searchKeys):
            outputValues[i] = getParam(key)
            # Print to debug
            printToDebug("URL found - %s = %s"%(key, str(outputValues[i])), **debugOptions)
    elif isinstance(searchKeys, str):
        outputValues = getParam(searchKeys)
        # Print to debug
        printToDebug("URL found - %s = %s"%(searchKeys, str(outputValues)), **debugOptions)
    else:
        outputValues = [None]
    return outputValues

def setURLParams(URLParamsAllowed, varSpace=globals(), **debugOptions):
    '''
    Set values for search keys passed from URL suffix
    CAUTION: ALLOWS SETTING OF VARIABLES!!!!!!!!!!
    '''
    # For debug
    debugOptions = editDebugPrefix(debugOptions)
    # Get parameters received from URL
    URLParams = getURLParams(URLParamsAllowed)
    # Set parameters received from URL
    for i, key in enumerate(URLParamsAllowed):
        # URL parameter/variable
        param = URLParams[i]
        # If valid URL parameter/variable
        if not param is None:
            # Get settings for variable
            content = URLParamsAllowed[key]
            if isinstance(content, dict):
                # If content is a dict, then...
                # Get type (required) and make variable that type - e.g. float
                if "type" in content:
                    contType = content["type"]
                    param = contType(param)
                else:
                    printToDebug("WARNING - Missing dict entry 'type' for key = "+key, debug, debugPrefix)
                # Defaults if no dict entries found
                vMin = None
                vMax = None
                vStep = None
                # Get min, max, and step values if dict entries exist
                # (converting to same "type" as main parameter value)
                if "min" in content: vMin = contType(content["min"])
                if "max" in content: vMax = contType(content["max"])
                if "step" in content: vStep = contType(content["step"])
                # Constrain variable value
                param = constrain(param, vMin, vMax, vStep)
            else:
                # Assume content is a type class and make variable that type
                contType = content
                param = contType(param)
            # Note: Below used to avoid use of exec (which works but is advised against, e.g. exec(key+"="+str(param)))
            # Split any a.b.c style syntax into components
            keySplit = str(key).split('.')
            # Depending on number of parts found...
            numKeySplit = len(keySplit)
            if numKeySplit == 1:
                # Just set variable name as parameter value (in varSpace function has been passed)
                varSpace[keySplit[0]] = param
            else:
                # Loop round parts getting next nested level...
                obj = varSpace[keySplit[0]]
                for i in range(1, numKeySplit-1):
                    obj = getattr(obj, keySplit[i])
                # ... Then finally assigning value at end
                setattr(obj, keySplit[-1], param)
            # Print to debug
            printToDebug("URL setting - %s = %s"%(key, str(param)), **debugOptions)

def sendCustomEvent(customEventName, **debugOptions):
    '''
    Send custom event with defined name
    (so can listen for this elsewhere)
    '''
    # For debug
    debugOptions = editDebugPrefix(debugOptions)
    # Print to debug
    printToDebug("Sending custom event = "+str(customEventName), **debugOptions)
    # Deprecated!
    # # Create and send custom event with defined name customEventName
    # e = document.createEvent("CustomEvent")
    # e.initEvent(customEventName, True, True)
    # document.dispatchEvent(e)
    e = js.CustomEvent.new("py:loaded")
    window.dispatchEvent(e)

def sendEvent(target, eventType, eventOptions={}, **debugOptions):
    '''
    Send event with defined type and optional content
    '''
    # For debug
    debugOptions = editDebugPrefix(debugOptions)
    # Print to debug
    debugStr = "Sending event type = "+str(eventType)
    if eventOptions and isinstance(eventOptions, dict):
        debugStr += ", options = "+str(eventOptions)
    printToDebug(debugStr, **debugOptions)
    # Create and send event
    e = js.Event.new(eventType)
    target.dispatchEvent(e)

def pcm2float(y, **debugOptions):
    '''
    Convert PCM data to float
    '''
    # For debug
    debugOptions = editDebugPrefix(debugOptions)
    #  if data type not float (note: bit hacky)
    if y.dtype != np.dtype('float64'):
        # Assume data type received indicates standard PCM encoding
        if y.dtype == np.dtype('int8'):
            nbit = 8
        elif y.dtype == np.dtype('int16'):
            nbit = 16
        elif y.dtype == np.dtype('int32'):
            nbit = 32
        else:
            () # TODO - Some data types not listed above
        # Print to debug
        printToDebug("Converting PCM to float using N = %i bits"%(nbit), **debugOptions)
        # Convert to float
        y = np.float64(y)*2**-(nbit-1)
    return y

