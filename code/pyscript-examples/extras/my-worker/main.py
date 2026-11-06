from pyscript import document, when, workers
import time

# Get elements from page
aNum = document.getElementById("num1Id")
bNum = document.getElementById("num2Id")
mainQuickButton = document.getElementById("runMainQuickButtonId")
mainSlowButton = document.getElementById("runMainSlowButtonId")
workerQuickButton = document.getElementById("runWorkerQuickButtonId")
workerSlowButton = document.getElementById("runWorkerSlowButtonId")
mainPara = document.getElementById("mainParagraphId")
workerPara = document.getElementById("workerParagraphId")

# Get the worker by name
myWorker = await workers["myWorker"]

'''
Run quick or slow blocks of code in main or worker thread and print result to screen
All are just a sum of two numbers on the page, but...
'slow' code includes blocking call to time.sleep to simulate much longer processing time
'''

# Run a very quick block of code (main thread)
@when("click", "#runMainQuickButtonId")
def runMainQuickButtonCalc(event):
    a = float(aNum.value)
    b = float(bNum.value)
    quickResult = a + b     # Just sum numbers
    mainPara.innerText = "a + b = " + str(quickResult)

# Run a time consuming block of code (main thread)
@when("click", "#runMainSlowButtonId")
def runMainSlowButtonCalc(event):
    a = float(aNum.value)
    b = float(bNum.value)
    time.sleep(5)           # Block for 5 seconds
    slowResult = a + b      # ... then sum numbers
    mainPara.innerText = "a + b = " + str(slowResult)

# Run a very quick block of code in worker thread
@when("click", "#runWorkerQuickButtonId")
async def runWorkerQuickButtonCalc(event):
    a = float(aNum.value)
    b = float(bNum.value)
    quickResult = await myWorker.quickCalc(a, b)    # Just sums numbers (but in worker)
    workerPara.innerText = "a + b = " + str(quickResult)

# Run a time consuming block of code in worker thread
@when("click", "#runWorkerSlowButtonId")
async def runWorkerQuickButtonCalc(event):
    a = float(aNum.value)
    b = float(bNum.value)
    quickResult = await myWorker.slowCalc(a, b)     # Sum/block in worker
    workerPara.innerText = "a + b = " + str(quickResult)

# Enable page buttons when ready
mainQuickButton.disabled = False
mainSlowButton.disabled = False
workerQuickButton.disabled = False
workerSlowButton.disabled = False

