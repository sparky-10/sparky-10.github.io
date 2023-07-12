from pyodide.ffi import to_js, create_proxy
from js import pyLoaded, pReply, imReply, passUserMessage
from js import document, Uint8Array
from js import console, Blob, URL
# from js import window

#import asyncio
import io
from pyFDTD.pyFDTD import pyFDTD

DEBUG = False
DEBUG_PREFIX = "PY: "
DO_PLOT = False  # I.e. matplotlib plot, not the js plotting
DO_SRC_REC_COORDS_CHECK = False     # Stops sources being deleted if go off image (handle in js instead)
LOAD_FILE_ID = "Load file"
GIF_DOWNLOAD_ID = "Gif download"
WAV_DOWNLOAD_ID = "Wav download"

if DEBUG: print("FDTD!")
# import os
# paths = {'/home/pyodide/images/'}
# paths = {'/', '/home/', '/home/pyodide/'}
# for path in paths:
#     print(path)
#     files = os.listdir(path)
#     for file in files: print(file)

# Init
fdtd = pyFDTD(debug=DEBUG, debugPrefix=DEBUG_PREFIX, doPlot=DO_PLOT)

fdtd.betaType == 'absorption'

#fdtd.delRec(0)      # Get rid of default receiver
fdtd.doSrcRecCoordsCheck = DO_SRC_REC_COORDS_CHECK

fdtd.saveRecData = False        # Gets set by user
fdtd.saveGif = False            # Gets set by user
# fdtd.fsOut = 44100              # Resample output before writing to wav
gifFile = 'fdtdAnimate.gif'
wavFile = 'fdtdAnimate.wav'

# Some settings from html elements (switching x and y to match definitions)
XMin = int(document.getElementById("Y grid").min)
XMax = int(document.getElementById("Y grid").max)
YMin = int(document.getElementById("X grid").min)
YMax = int(document.getElementById("X grid").max)

# Send pressures back when requested
def doPRequest():
    pReply(to_js(fdtd.p))
    
# Send image array back when requested
def doImRequest():
    imReply(to_js(fdtd.mesh))

# General attribute request
def doAttRequest(value, attr, ind=0):
    values = getattr(fdtd, attr)
    values[ind] = value
    setattr(fdtd, attr, values)

# Create output files as io bytes objects
def doCreateOPFile():
    fdtd.recDataFile = io.BytesIO()
    fdtd.gifFile = io.BytesIO()

# Add a source
def srcAdd(x, y):
    fdtd.addSrc([x, y])

# Move the source
def srcMove(x, y, i):
    #if debug: print('%f, %f, %i'%(x,y,i))
    fdtd.moveSrc([x, y],i)

# Add a source
def recAdd(x, y):
    fdtd.addRec([x, y])

# Move the source
def recMove(x, y, i):
    #if debug: print('%f, %f, %i'%(x,y,i))
    fdtd.moveRec([x, y],i)
    
# Load the image data or file to FDTD
def loadImage(im):
    # Pass to fdtd for use with PIL (includes reset etc...)
    padOrTrim = fdtd.loadImage(im, doReset=True, \
                               sizeLimits=[XMin, XMax, YMin, YMax])
    if padOrTrim:
        passUserMessage("Image pad/truncation warning")
    # Empty file value so reloads on reselection of same file (i.e. because a change occurs)
    document.getElementById(LOAD_FILE_ID).value = ''
    # Make initial 'mesh' version
    #fdtd.image2Mesh(threshold=None, addToPlot=False)
    # Pass to js
    doImRequest()

# Get numpy array from image file
# (code adapted from https://jeff.glass/post/pyscript-image-upload/)
async def getNewImage(e):
    # Stop sim
    fdtd.stop()
    # Get the first file from upload
    file_list = e.target.files
    first_item = file_list.item(0)
    # Get the data from the files arrayBuffer as an array of unsigned bytes
    array_buf = Uint8Array.new(await first_item.arrayBuffer())
    # BytesIO wants a bytes-like object, so convert to bytearray first
    bytes_list = bytearray(array_buf)
    my_bytes = io.BytesIO(bytes_list)
    # Load the image
    loadImage(my_bytes)

async def gifDownload(e):
    try:
        # Get file type
        file = gifFile
        buf = fdtd.gifFile
        blobType = "image/gif"
        # fileType = file.split('.')[-1]
        # if fileType == "gif":
        #     blobType = "image/"+fileType
        # elif fileType == "wav":
        #     blobType = "audio/wav; codecs=MS_PCM"
        # Read and convert to a JavaScript array
        buf.seek(0)
        content = to_js(buf.read())
        # Create a JavaScript Blob and set the Blob type
        b = Blob.new([content], {type: blobType})
        # # File system save - using file picker
        # fileHandle = await window.showSaveFilePicker()
        # file = await fileHandle.createWritable()
        # await file.write(b)
        # await file.close()
        # File system save - using file picker
        tag = document.createElement('a')
        tag.href = URL.createObjectURL(b)
        tag.download = file
        tag.click()
    except Exception as e:
        console.log("Exception: " + str(e))
        return

async def wavDownload(e):
    try:        
        file = wavFile
        buf = fdtd.recDataFile
        blobType = "audio/wav"
        buf.seek(0)
        content = to_js(buf.read())
        b = Blob.new([content], {type: blobType})
        tag = document.createElement('a')
        tag.href = URL.createObjectURL(b)
        tag.download = file
        tag.click()
    except Exception as e:
        console.log("Exception: " + str(e))
        return

# Run get new image code above whenever file is uploaded    
upload_file = create_proxy(getNewImage)
document.getElementById(LOAD_FILE_ID).addEventListener("change", upload_file)

# Do downloads when get button clicks
gifProxy = create_proxy(gifDownload)
document.getElementById(GIF_DOWNLOAD_ID).addEventListener("click", gifProxy)
wavProxy = create_proxy(wavDownload)
document.getElementById(WAV_DOWNLOAD_ID).addEventListener("click", wavProxy)

# Message to js to say loaded
pyLoaded()

