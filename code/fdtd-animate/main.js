
// Settings
var DEBUG = false;
var debugPrefix = "JS: ";
var meshImageFolder = "/home/pyodide/images/";
var mainHeaderPrefix = "FDTD Animate : ";
var plotDivId = "fdtdPlot";
var altModebarDivId = "Alt modebar";
var imageSaveName = "fdtdAnimate";
var imgDivId = "Temp img";
var srcTableID = "Source table";
//var recTableID = "Receiver table";
var recTableID = srcTableID;
var tSimDivID = "Sim time div";
var gridMin = 10;
var gridMax = 1000;
var fdtdFigLayer = 0;
var meshFigLayer = 1;
var srcFigLayer = 2;
var recFigLayer = 3;
var plotSleepTime = 0.01;	// ms
var plotWidthRelToWindow = 1.0;
var plotHeightRelToWindow = 0.75;
var maxSteps = Infinity;
//var rWeight = 0.2126, gWeight = 0.7152, bWeight = 0.0722; // Luminance = Photometric/digital ITU BT.709
//var rWeight = 0.299, gWeight = 0.587, bWeight = 0.114; // Luminance = Digital ITU BT.601
var updateOL = true;		// Update offline checkbox
var resetOnOLUpdate = true;	// Set (local) p data back to zero where makes sense
var checkAndFixMesh = true;	// Check and attempt to fix mesh before running
var gifDownload = false;
var wavDownload = false;
var gifFrameTime = 50;		// ms
var gifLoopNum = 0;			// 0 = infinite
var doAbsCoeff = false;		// If beta values are actually NIAC (false because now handled in Python)
var renderPanZoom = true;	// Include pan/zoom in rendering of new plot/mesh
var discretiseInputs = true;// Discretise user inputs using step value
var limitFreq = true; 		// Limit source frequency
var loadEx = "";			// Don't load anything

var infoText = 	"Info:\n-----\n"+
				"\n"+
				"2D acoustic Finite Difference Time Domain (FDTD) simulation.\n"+
				"Richard Hughes ( r.j.hughes@salford.ac.uk ; @sparky_10 )\n"+
				"\n"+
				"Make and simulate a 2D sound world from an image. "+
				"Mainly a bit of fun, but also for interest/understanding.\n"+
				"\n"+
				"Uses PyScript (https://pyscript.net/) to download and run Python code. "+
				"Python not required, but takes a short while to load and "+
				"data is on order of tens of MB. "+
				"PyScript is developmental and constantly changing; I'll try to make sure it doesn't break!\n"+
				"\n"+
				"If of interest:\n"+
				"- Grid: basic rectangular\n"+
				"- Scheme: compact explicit standard leapfrog\n"+
				"- See e.g.: work of Konrad Kowalczyk\n"+
				"- Source(s): Gaussian derivative\n"+
				"- Boundary: no perfectly matched layer (PML)!!\n"+
				"\n"+
				"Disclaimer:\n"+
				"Content on this site provided solely for fun. 'Use at your own risk'. "+
				"No guarantee made of accurate predictions and should not be relied on.";

// Some stuff that might override html values
var cn = [0, 	0, 		255];	// Negative colour
var cz = [255, 	255,	255];	// Zero colour
var cp = [255, 	0, 		0];		// Positive colour
var cLim = 0.1;
var meshShowStatus = true;
var srcShowStatus = true;
var recShowStatus = true;
var meshColInvStatus = false;
var NxDefault = 300;
var NyDefault = 200;
var XDefault = 10.0;
var NSrc = 4;
var NRec = 1;
var srcTypeDefault = "";		// Default set by function
var srcPeriodsDefault = 2;
var cDefault = 344.0;
var tDefault = 10.0;
var betaDefault = 0.0;
var betaBorderDefault = 0.0;
var imageThresholdDefault = 5;
var betaModeDefault = "constant";
var cnDefault = [...cn], czDefault = [...cz], cpDefault = [...cp];
var cLimDefault = cLim;
var meshShowDefault = meshShowStatus;
var srcShowDefault = srcShowStatus;
var recShowDefault = recShowStatus;
var meshColInvDefault = meshColInvStatus;

// From URL (in case any options)
// E.g. URL/?debug=1&gridMax=2000
const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
if (urlParams.has("debug")) {
	DEBUG = Boolean(Number(urlParams.get("debug")));
	printToDebug("URL param: debug = "+(DEBUG));
}
if (urlParams.has("gridMin")) {
	gridMin = Number(urlParams.get("gridMin"));
	gridMin = clamp(gridMin, 2, 1000);
	printToDebug("URL param: gridMin = "+(gridMin));
}
if (urlParams.has("gridMax")) {
	gridMax = Number(urlParams.get("gridMax"));
	gridMax = clamp(gridMax, gridMin, 10000);
	printToDebug("URL param: gridMax = "+(gridMax));
}
if (urlParams.has("numSrc")) {
	NSrc = Number(urlParams.get("numSrc"));
	NSrc = clamp(NSrc, 4, 100);
	printToDebug("URL param: numSrc = "+(NSrc));
}
if (urlParams.has("numRec")) {
	NRec = Number(urlParams.get("numRec"));
	NRec = clamp(NRec, 1, 100);
	printToDebug("URL param: numRec = "+(NRec));
}
if (urlParams.has("discInputs")) {
	discretiseInputs = Boolean(Number(urlParams.get("discInputs")));
	printToDebug("URL param: discInputs = "+(discretiseInputs));
}
if (urlParams.has("limitFreq")) {
	limitFreq = Boolean(Number(urlParams.get("limitFreq")));
	printToDebug("URL param: limitFreq = "+(limitFreq));
}
if (urlParams.has("load")) {
	loadEx = urlParams.get("load");
	loadEx = loadEx.replace(/-+/g, ' ');
	printToDebug("URL param: load = "+(loadEx));
}
if (urlParams.has("srcType")) {
	srcTypeDefault = urlParams.get("srcType");
	srcTypeDefault = srcTypeDefault.replace(/-+/g, ' ');
	printToDebug("URL param: srcType = "+(srcTypeDefault));
}
if (urlParams.has("srcPeriods")) {
	srcPeriodsDefault = Number(urlParams.get("srcPeriods"));
	srcPeriodsDefault = clamp(Math.round(srcPeriodsDefault), 1, 100);
	printToDebug("URL param: srcPeriods = "+(srcPeriodsDefault));
}

// Other variables
var zValues;
var data, layout;
var runReset, runStep;
var pyZValues, xValues, yValues;
var pyValidStep;
var colorscaleValue, colorscaleGrey, bgColour;
var stopNextStep, isRunning = false;
var nextHeaderUpdate = mainHeaderPrefix + "Ready!!";
var X, Nx, Ny, Dx, Dy, c, t, plotIthUpdate, tSim;
var imageThreshold, betaMode, beta, betaBorder;
var srcActive = Array(NSrc).fill(0);	// Source stuff will get replaced
var srcX = Array(NSrc).fill(0);
var srcY = Array(NSrc).fill(0);
var srcAmp = Array(NSrc).fill(1);
var srcInv = Array(NSrc).fill(0);
var srcDelay = Array(NSrc).fill(0);
var srcFreq = Array(NSrc).fill(0);
var srcType = Array(NSrc).fill(0);
var srcActiveDefault, srcXDefault, srcYDefault, srcAmpDefault, srcInvDefault, srcDelayDefault, srcFreqDefault;
var srcXRel = Array(NSrc).fill(0), srcYRel = Array(NSrc).fill(0), srcStep;
var recActive = Array(NRec).fill(0);	// Receiver stuff will get replaced
var recX = Array(NRec).fill(0);
var recY = Array(NRec).fill(0);
var recActiveDefault, recXDefault, recYDefault;
var recXRel = Array(NRec).fill(0), recYRel = Array(NRec).fill(0), recStep;
var figExists = false;
var initialising = true;
var imReplyResetPlot = true;
var gsArray;
var plotWidth, plotHeight
var srcActiveBox = [], srcXBox = [], srcYBox = [], srcAmpBox = [], srcInvBox = [], srcDelayBox = [], srcFreqBox = [];
var recActiveBox = [], recXBox = [], recYBox = [];
var srcTxt = [], recTxt = [];
var exampleList, imExt;
var madeGif, madeWav;

/* TODO
- Add 'saving' text
- Add modes example
- Chrome pyScript issue?
- Test on larger screen
- Move source - callback on marker click to move?? OR use shapes for source/receivers??
- Always
	- Test examples thouroughly
	- DEBUG = FALSE!!!!!
- Save GIF
	- Any user gif settings?
	- Add sources (more difficult)
- Move pyFDTD to submodule respository?? NO!
- Show 'loading' when loading examples - hard to fix
- Make loadExample more efficient? (i.e. triggering less stuff)
- Load own source
- Add offset to padding/trimming

ONGOING:
- Aspect ratio - have ugly fix for this
- HTML pretty-fy
- Pyscript version update
- Plotly version update
- New examples

DOUBLE-CHECK (i.e. think working)
- Do absorbcoeff in Python (and make sure does for both constant and varying)
- Check source freq limits
- Fix mesh
- Valid source position (/warn when not)
- Auto update = false
- Multi-Source
- Warning when image too big or small (inc. pad/trim)
- Pad/trim (user specified)
- Source on surface
- Admittance stuff
*/

// Main header
var mainHeader = document.getElementById("Main header");
mainHeader.innerHTML = mainHeaderPrefix + "Loading...";

// Input boxes
var plotDiv 		= document.getElementById(plotDivId);
var altModebarDiv 	= document.getElementById(altModebarDivId);
var imgDiv 			= document.getElementById(imgDivId);
var srcTable 		= document.getElementById(srcTableID);
var recTable 		= document.getElementById(recTableID);
var tSimDiv			= document.getElementById(tSimDivID);
//var srcXBox 		= document.getElementById("Src X");
//var srcYBox 		= document.getElementById("Src Y");
var OLUpdateBox		= document.getElementById("OL plot update");
var OLMeshCheckBox	= document.getElementById("Mesh check");
var downloadGifBox	= document.getElementById("Download gif");
var downloadWavBox	= document.getElementById("Download wav");
var XGridBox 		= document.getElementById("X grid");
var YGridBox 		= document.getElementById("Y grid");
var gridSpacingBox 	= document.getElementById("Grid spacing");
var soundSpeedBox 	= document.getElementById("Sound speed");
var simTimeBox 		= document.getElementById("Sim time");
var plotStepBox 	= document.getElementById("Plot step");
var cnrBox 			= document.getElementById("cnr");
var cngBox 			= document.getElementById("cng");
var cnbBox 			= document.getElementById("cnb");
var czrBox 			= document.getElementById("czr");
var czgBox 			= document.getElementById("czg");
var czbBox 			= document.getElementById("czb");
var cprBox 			= document.getElementById("cpr");
var cpgBox 			= document.getElementById("cpg");
var cpbBox 			= document.getElementById("cpb");
var cLimBox 		= document.getElementById("cLim");
var meshShowBox 	= document.getElementById("Mesh show");
var srcShowBox 		= document.getElementById("Source show");
var recShowBox 		= document.getElementById("Receiver show");
var meshColInvBox	= document.getElementById("Mesh colour invert");
var loadFileBox 	= document.getElementById("Load file");
var betaBox			= document.getElementById("Beta mesh");
var betaBorderBox	= document.getElementById("Beta boundary");
var imThreshBox		= document.getElementById("Image threshold");
var imThreshSlider	= document.getElementById("Threshold slider");
var betaModeBox		= document.getElementById("Beta mode");
var examplesBox		= document.getElementById("Load examples");
var gifDownloadBut 	= document.getElementById("Gif download");
var wavDownloadBut 	= document.getElementById("Wav download");
var srcTypeAllBox	= document.getElementById("Source type all");
var srcPeriodsAllBox= document.getElementById("Source periods all");

// Set stuff
OLUpdateBox.checked = updateOL;
OLMeshCheckBox.checked = checkAndFixMesh;
downloadGifBox.checked = gifDownload;
downloadWavBox.checked = wavDownload;
XGridBox.min = gridMin;
XGridBox.max = gridMax;
YGridBox.min = gridMin;
YGridBox.max = gridMax;
tSimDivUpdate(0.0);		// Sim time is zero
defineExamples();		// Define the loadable examples dropdown list
defineSrcTypes();		// define dropdown source type options
makeSrcTable();			// Make a table with all the source parameter inputs
makeRecTable();			// Make a table with all the receiver parameter inputs - not really a table, but to stick with same format as sources
defineSrcDefaults();	// Define the default source values
defineRecDefaults();	// Define the default receiver values
setBoxDefaults();		// Set defaults

// Print to debug, including prefix (if DEBUG == true)
function printToDebug(txt) {
	if (DEBUG) {
		var debugText = debugPrefix;
		debugText += txt;
		console.log(debugText);
	}
}

// Pass message to user in form of an alert
function passUserMessage(txt) {
	printToDebug("Received user message");
	alert(txt);
}

// Sleep
function sleep(ms) {
	return new Promise(resolve => setTimeout(resolve, ms));
}

// Linspace vector
function linspace(start, stop, num, endpoint = true) {
	if (num > 1) {
		const div = endpoint ? (num - 1) : num;
		const step = (stop - start) / div;
		return Array.from({length: num}, (_, i) => start + step * i);
	} else if (endpoint) {
		return [0.5*(start+stop)]
	} else {
		return [start]
	}
}

// Get random integer
function getRandomInt(max) {
  return Math.floor(Math.random() * max);
}

// Get values in array where logical array is true
function whereIsTrue(input, logicalArray) {
	var inds = [];
	logicalArray.forEach( (val, index) => { if(val) { inds.push(index); } });
	return inds.map(i => input[i]);
}

// Update sim time div text
function tSimDivUpdate(tSim=null) {
	if (tSim == null) { tSim = fdtdObj.loopNum*fdtdObj.T; }
	tSim = tSim*1e3;						// In ms
	tSim = tSim.toFixed(2).toString();		// To 2 d.p.
	tSim = tSim.padStart(8);				// Pad to length
	tSimDiv.innerHTML = "t = "+tSim+" ms"	// Update
}

// Clamp a number
function clamp(num, min, max) {
	return Math.max(Math.min(num,max),min);
}

// Ensure value is in range and return value
function constrainInput(obj, val=null) {
	return new Promise(function(resolve, reject) {
		if (obj==null) { val = null }
		else {
			if (val==null) { val = obj.value }
			if (discretiseInputs) {
				val = Math.round(val/obj.step)*obj.step;	// Round to nearest step
			}
			val = clamp(val,obj.min,obj.max);				// Limit to range
			obj.value = val;
		}
		resolve(val);
	});
};

// Convert (normal incidence) absorption coefficient to admittance
function abs2admit(alpha) {
	// Reflection coefficient
	var R = Math.sqrt(1-alpha)
	var admit = (1-R)/(1+R);
	return admit;
}

// Clear file from file loader
function clearFile() {
	return new Promise(function(resolve, reject) {
		loadFileBox.value = null;
		resolve(loadFileBox.value);
	});
}

// Receive p data from python
function pReply(pIn) {
	printToDebug("received p data");
	pyZValues = pIn
}

// Receive image data from Python
function imReply(imIn) {
	printToDebug("Received image data");
	gsArray = imIn;
	// Update grid inputs
	XGridBox.value = gsArray[0].length;
	YGridBox.value = gsArray.length;
	// Update grid size
	olGridSizeUpdate(false);
	// Rest all (does a p request, plus a couple of other things)
	if (imReplyResetPlot) {
		resetAll();										// Makes new fig
	} else {
		resetAll(false);								// No new fig
		updateFigData({'z': [gsArray]}, meshFigLayer);	// Update fig image
	}
	imReplyResetPlot = true;
	// Get p Data
	//pyPRequest();
	// Remake figure
	//makeFig();
	// Update header
	//mainHeader.innerHTML = mainHeaderPrefix + "Ready!!";		// Does this in resetAll()
}

// Reset (to empty) mesh
function resetMesh() {
	printToDebug("Reset mesh");
	// Reset mesh
	fdtdObj.meshReset();
	// Clear image (so any mesh size updates don't trigger a reloading of old image)
	fdtdObj.image = null;
	// Ping to get image back and reset everything here
	pyImRequest();
}

// Check (and fix) mesh
function checkMesh() {
	printToDebug("Check mesh");
	if (checkAndFixMesh) {
		var meshChanged = fdtdObj.checkMesh();
		if (meshChanged) {
			pyImRequest();
		}
	}
}

// Set download status in Python
function downloadStatus() {
	printToDebug("Download status Python updates");
	// Set status of making files in Python
	fdtdObj.saveGif = gifDownload;
	fdtdObj.saveRecData = wavDownload;
	// Store incase check boxes change mid sim
	madeGif = gifDownload;
	madeWav = wavDownload;
	// Reset output files in Python
	pyCreateOPFile();
	// Set relevant Python real time JS stuff (with subsequent real time changes having no effect)
	// Plot update
	fdtdObj.plotIthUpdate = plotIthUpdate;
	// Colour limits
	pyAttRequest(-cLim, 'cLims', 0);
	pyAttRequest(+cLim, 'cLims', 1);
	// Pass colour scale and update
	for (let i = 0; i < 3; i++) {
		pyAttRequest(cz[i]/255, 'c0', i);
		pyAttRequest(cn[i]/255, 'c1', i);
		pyAttRequest(cp[i]/255, 'c2', i);
	} 
	fdtdObj.setCMap();
	// Surface show/hide and colour invert
	fdtdObj.plotShowMask = meshShowStatus
	fdtdObj.plotMaskColInvert = meshColInvStatus
	// GIF settings
	fdtdObj.gifFrameTime = gifFrameTime;
	fdtdObj.gifLoopNum = gifLoopNum;
	// NOTE: for future
	// Show/hide sources/receivers
	fdtdObj.plotShowSrc = srcShowStatus
	fdtdObj.plotShowRec = recShowStatus
	// Required to init gif (even if doPlot is set to false)
	fdtdObj.makePlot()
}

// Get colour array (for FDTD)
function getColorScale() {
	printToDebug("Get colour scale");
	var rgbNeg 	= `rgb(${cn[0]}, ${cn[1]}, ${cn[2]})`;
	var rgbZero = `rgb(${cz[0]}, ${cz[1]}, ${cz[2]})`;
	var rgbPos 	= `rgb(${cp[0]}, ${cp[1]}, ${cp[2]})`;
	colorscaleValue = [
		['0.000', rgbNeg],
		['0.500', rgbZero],
		['1.000', rgbPos]
	];
	bgColour = rgbZero;
}

// Get greyscale array (for mesh)
function getGreyScale() {
	printToDebug("Get grey scale");
	if (!meshColInvStatus) {
		// Rigid surfaces are black
		colorscaleGrey = [
			['0.000', 'rgba(255, 255, 255, 0)'], // Transparent when completely white
			['0.005', 'rgba(254, 254, 254, 1)'],
			['1.000', 'rgba(000, 000, 000, 1)']
		]
	} else {
		// Rigid surfaces are white
		colorscaleGrey = [
			['0.000', 'rgba(000, 000, 000, 0)'], // Transparent when completely black
			['0.005', 'rgba(001, 001, 001, 1)'],
			['1.000', 'rgba(255, 255, 255, 1)']
		]
	}
}

// Define source defaults
function defineSrcDefaults() {
	printToDebug("define source defaults");
	// Source active
	srcActiveDefault = Array(NSrc).fill(false);
	srcActiveDefault[0] = true
	// Source amplitude
	srcAmpDefault = Array(NSrc).fill(1.0);
	// Source inverted
	srcInvDefault = Array(NSrc).fill(false);
	// Source delay
	srcDelayDefault = Array(NSrc).fill(0.0);
	// Source centre frequency (relative to sample rate)
	srcFreqDefault = Array(NSrc).fill(0.075*1/3);
	// Source x coord
	var X = NxDefault*XDefault*1e-3;
	srcXDefault = linspace(X*0.25, X*0.75, NSrc, true);
	// Source y coord
	var Y = NyDefault*XDefault*1e-3;
	srcYDefault = Array(NSrc).fill(Y*0.5);
}

// Define receiver defaults
function defineRecDefaults() {
	printToDebug("define receiver defaults");
	// Receiver active
	recActiveDefault = Array(NRec).fill(false);
	recActiveDefault[0] = true;
	// Receiver x coord
	var X = NxDefault*XDefault*1e-3;
	recXDefault = Array(NRec).fill(X*0.5);
	// Receiver y coord
	var Y = NyDefault*XDefault*1e-3;
	recYDefault = linspace(Y*0.25, Y*0.75, NRec, true);
}


// Set defaults (just updates boxes)
function setBoxDefaults() {
	printToDebug("Set defaults");
	// Set grid settings
	XGridBox.value = NxDefault;
	YGridBox.value = NyDefault;
	gridSpacingBox.value = XDefault;
	soundSpeedBox.value = cDefault;
	simTimeBox.value = tDefault;
	betaBox.value = betaDefault;
	betaBorderBox.value = betaBorderDefault;
	imThreshBox.value = imageThresholdDefault;
	imThreshSlider.value = imageThresholdDefault;
	betaModeBox.value = betaModeDefault;
	// Set sources
	setSrcBoxSettings(	srcActiveDefault,
						srcXDefault, 
						srcYDefault,	
						srcAmpDefault, 
						srcInvDefault, 
						srcDelayDefault,
						srcFreqDefault);
	// Set receivers
	setRecBoxSettings(	recActiveDefault, 
						recXDefault, 
						recYDefault);
	// Plus real-time stuff where appropriate
	cLimBox.value = cLimDefault;
	meshShowBox.checked = meshShowDefault;
	srcShowBox.checked = srcShowDefault;
	recShowBox.checked = recShowDefault;
	meshColInvStatus.checked = meshColInvDefault;
}

// Set source box settings
function setSrcBoxSettings(act, x, y, amp, inv, del, freq) {
	printToDebug("Set source box settings");
	var N = act.length;
	for (var i = 0; i<N; i++){
		srcActiveBox[i].checked = act[i];
		srcXBox[i].value = x[i];
		srcYBox[i].value = y[i];
		srcAmpBox[i].value = amp[i];
		srcInvBox[i].checked = inv[i];
		srcDelayBox[i].value = del[i];
		srcFreqBox[i].value = getSrcFreq(freq[i])
	}
}

// Set receiver box settings
function setRecBoxSettings(act, x, y) {
	printToDebug("Set receiver box settings");
	var N = act.length;
	for (var i = 0; i<N; i++){
		recActiveBox[i].checked = act[i];
		//recActiveBox[i].checked = false;									// Temp deactivates all receivers while debugging
		recXBox[i].value = x[i];
		recYBox[i].value = y[i];
	}
}

// Get source frequency from relative frequency
function getSrcFreq(relFreq) {
	var cVal = Number(soundSpeedBox.value);
	var XVal = Number(gridSpacingBox.value)*1e-3;
	var lam = 1/Math.sqrt(2);
	// This should be the simulation sample rate once everything is updated
	var fs = Math.round(cVal/(lam*XVal))
	var freq = Math.round(relFreq*fs);
	return freq;
};

// Set limits of frequency boxes
function setFreqBoxLims() {
	// get max frequency want to allow
	var lam = 1/Math.sqrt(2);
	var fs = Math.round(c/(lam*X));
	if (limitFreq) { 	var freqMax = Math.round(0.075*0.75*fs/10)*10; 	}
	else { 				var freqMax = Math.floor(fs/20)*10; 			}
	// Loop round sources and set
	for (var i = 0; i<NSrc; i++){
		fCurrent = Number(srcFreqBox[i].value);
		srcFreqBox[i].max = freqMax;
		if (fCurrent>freqMax) {
			srcFreqBox[i].value = freqMax;
			olSrcSettingsUpdate(false);		// No resetting etc as should be triggered by function that has already done this
		};
	};
}

// Define source types
function defineSrcTypes() {
	printToDebug("Define source types");
	// Define list
	var srcTypeList = [	"Gauss", "Gauss derivative 1", "Gauss derivative 2", "Gauss derivative 3", 
						"Tone", "Tone pulse", "Impulse"];
	// Add to select box
	for (var i = 0; i<srcTypeList.length; i++){
		var opt = document.createElement('option');
		opt.value = i;
		opt.innerHTML = srcTypeList[i];
		srcTypeAllBox.appendChild(opt);
	}
	// Default
	srcTypeAllBox.value = 1;
	for (var i = 0; i<srcTypeList.length; i++){
		srcTypeTxt = srcTypeDefault.toLowerCase();
		if (srcTypeAllBox.options[i].text.toLowerCase() == srcTypeTxt) {
			srcTypeAllBox.value = i;
		}
	}
	srcPeriodsAllBox.value = srcPeriodsDefault;
	// Update values
	olSrcTypeAllUpdate();
}

// Define examples
function defineExamples() {
	printToDebug("Define examples");
	// Add examples to list
	exampleList = ["Reset all", "Monopole", "Doublet", "Dipole", "Line array", "Beam steering",
						"Flat wall", "Absorbing wall", "Concave wall", "Convex wall", 
						"Schroeder diffuser", "Binary amplitude diffuser", "Helmholtz resonator",
						"Box room", "Whispering gallery", "Square object", "Circular object", "Barrier",
						"Single slit", "Double slit", "Perforated sheet", "Sonic crystal", 
						"Squiggle", "Hello world", "Maze"];
	imExt = "png";
	var numExample = exampleList.length;
	for (var i = 0; i<numExample; i++){
		var opt = document.createElement('option');
		opt.value = i;
		opt.innerHTML = exampleList[i];
		examplesBox.appendChild(opt);
	}
}

// Load example
function loadExample(loadTxt=null) {
	//printToDebug("Load example");
	// Attempt to load example if passed one
	if (loadTxt != null) {
		loadTxt = loadTxt.toLowerCase();
		var foundExample = false;
		for (var i = 0; i < examplesBox.options.length; i++) {
			if (examplesBox.options[i].text.toLowerCase() == loadTxt) {
				examplesBox.selectedIndex = i;
				foundExample = true;
				break;
			}
		}
		if (!foundExample) {
			// Return if not a match
			return;
		}
	}
	// Example to load
	var exNum = Number(examplesBox.value);
	var exTxt = examplesBox.options[examplesBox.selectedIndex].text;
	printToDebug("Load example: "+exTxt);
	// Stop everything
	stopButton(false);							// Stop without Reset
	//resetAll(false);							// Reset without re-plot
	// Temp set offline update to true
	var currentUpdateOL = updateOL;
	updateOL = true;
	// Set to defaults (if not "Load text")
	if (exNum < 0) {
		return;
	}
	// Update header
	mainHeader.innerHTML = mainHeaderPrefix + "Loading...";
	nextHeaderUpdate = mainHeader.innerHTML;
	// Set all input boxes to defaults
	setBoxDefaults();
	// Define admittance
	switch (exTxt) {
		case "Box room":
		case "Whispering gallery":
			// Any of the above get here using fall through
			betaBox.value = 0.0;
			betaBorderBox.value = 0.0;
			break;
		case "Absorbing wall":
			betaBox.value = 0.95;
			betaBorderBox.value = 1.0;
			break;
		case "Binary amplitude diffuser":
			betaModeBox.value = "varying";
			betaBorderBox.value = 1.0;
			break;
		default:
			// Otherwise
			betaBox.value = 0.0;
			betaBorderBox.value = 1.0;
	}
	// Update (so has immediate effect for loaded image)
	olMeshSettingsUpdate(false);	// No resetting / plot updates
	setMeshValues(false);			// No meshing / triggering replotting etc.
	// If anything wants different grid spacing, and/or non-image examples want different grid size
	switch (exTxt) {
		case "Helmholtz resonator":
			gridSpacingBox.value = 1;	// mm
			break;
		case "Box room":				// Fall through
		case "Barrier":					// Fall through
		case "Whispering gallery":
			gridSpacingBox.value = 20;	// mm
			break;
	}
	// Define grid size for non-image based examples or load image
	switch (exTxt) {
		case "Reset all":
			// Update
			olGridSizeUpdate(false);	// Update grid size (without plotting)
			setValues();				// Pass updates to Python
			resetMesh();				// Set blank mesh and trigger re-plotting
			break;
		case "Monopole":				// Fall through
		case "Doublet":					// Fall through
		case "Dipole":					// Fall through
		case "Line array":				// Fall through
		case "Beam steering":
			XGridBox.value = 300;
			YGridBox.value = 250;
			// Update
			olGridSizeUpdate(false);	// Update grid size (without plotting)
			setValues();				// Pass updates to Python
			resetMesh();				// Set blank mesh and trigger re-plotting
			break;
		// case 		// Anything here wanting to alter grid spacing (without break so also does default)
		default:
			// File name based on example name
			var fileStr = meshImageFolder+exTxt.replaceAll(" ","_")+"."+imExt;
			// Double sim time as standard
			switch (exTxt) {
				case "Barrier":
					simTimeBox.value = tDefault*2;
					break;
				case "Box room":				// Fall through
				case "Whispering gallery":		// Fall through
				case "Maze":
					simTimeBox.value = tDefault*3;
					break;
				case "Helmholtz resonator":
					simTimeBox.value = tDefault*0.5;
					break;
				default:
					simTimeBox.value = tDefault*1.5;
			};
			// Pass file name to Python to load (triggers replotting, updates grid size etc..)
			pyLoadImage(fileStr);
	}
	// So have correct speed of sound
	olGridStepUpdate(false);					// No resetting
	// Get some basics to base examples on
	var XX = Number(XGridBox.value);
	var YY = Number(YGridBox.value);
	var dx = Number(gridSpacingBox.value)*1e-3;
	var XMid = (XX-1)*dx*0.5;
	var YMid = (YY-1)*dx*0.5;
	var dSrc = 16*dx;
	var dSlit = 10*dx;
	var dPerf = 10*dx;
	var srcDel = Math.round(10*0.5*dSrc/c*1e3)*0.1;
	var lam = 1/Math.sqrt(2);
	var fs = Math.round(c/(lam*dx))
	// Set remaining parameters
	switch (exTxt) {
		case "Reset all":
			break;
		case "Monopole":
			setSrcBoxSettings(	[true], 
								[XMid], [YMid], 
								[1.0], [false], 
								[0.0], [srcFreqDefault[0]]);
			setRecBoxSettings(	[true], [XMid*1.5], [YMid]);
			break;
		case "Doublet":
			var lambda = dSrc*2;
			var relFreq = (c/lambda)/fs;
			setSrcBoxSettings(	[true, true], 
								[XMid, XMid], [YMid+dSrc*0.5, YMid-dSrc*0.5],
								[1.0, 1.0], [false, false], 
								[0.0, 0.0], [relFreq, relFreq]);
			setRecBoxSettings(	[true], [XMid*1.5], [YMid]);
			cLimBox.value = cLimDefault*1.5;
			break;
		case "Dipole":
			var lambda = dSrc*2;
			var relFreq = (c/lambda)/fs;
			setSrcBoxSettings(	[true, true],
								[XMid, XMid], [YMid+dSrc*0.5, YMid-dSrc*0.5],
								[1.0, 1.0], [false, true], 
								[0.0, 0.0], [relFreq, relFreq]);
			setRecBoxSettings(	[true], [XMid*1.5], [YMid]);
			cLimBox.value = cLimDefault*1.5;
			break;
		case "Line array":
			var lambda = dSrc*2;
			var relFreq = (c/lambda)/fs;
			var y1 = YMid+dSrc*(1-NSrc)*0.5;
			var y2 = YMid+dSrc*(NSrc-1)*0.5;
			setSrcBoxSettings(	Array(NSrc).fill(true), 
								Array(NSrc).fill(XMid), linspace(y1, y2, NSrc, true),
								Array(NSrc).fill(1.0), Array(NSrc).fill(false),
								Array(NSrc).fill(0.0), Array(NSrc).fill(relFreq));
			setRecBoxSettings(	[true], [XMid*1.5], [YMid]);
			cLimBox.value = cLimDefault*2;
			break;
		case "Beam steering":
			var lambda = dSrc*2;
			var relFreq = (c/lambda)/fs;
			var y1 = YMid+dSrc*(1-NSrc)*0.5;
			var y2 = YMid+dSrc*(NSrc-1)*0.5;;
			setSrcBoxSettings(	Array(NSrc).fill(true), 
								Array(NSrc).fill(XMid), linspace(y1, y2, NSrc, true),
								Array(NSrc).fill(1.0), Array(NSrc).fill(false), 
								linspace(0, (NSrc-1)*srcDel, NSrc, true), Array(NSrc).fill(relFreq));
			setRecBoxSettings(	[true], [XMid*1.5], [YMid]);
			cLimBox.value = cLimDefault*2;
			break;
		case "Whispering gallery":
			setSrcBoxSettings(	[true], 
								[XMid], [(YY-1-4)*dx],
								[1.0], [false], 
								[0.0], [srcFreqDefault[0]]);
			setRecBoxSettings(	[true], [XMid], [4*dx]);
			cLimBox.value = cLimDefault*2.5;
			break;
		case "Helmholtz resonator":
			var resFreq = 2000/fs;
			//var resFreq = srcFreqDefault[0];
			setSrcBoxSettings(	[true], 
								[XMid], [(YY-1)*dx*0.666],
								[1.0], [false], 
								[0.0], [resFreq]);
			setRecBoxSettings(	[true], [XMid], [(YY-1)*dx*0.5]);
			break;
		case "Single slit":			// Fall through
		case "Double slit":
			var lambda = dSlit*2;
			var relFreq = (c/lambda)/fs;
			setSrcBoxSettings(	[true], 
								[(XX-1)*dx*0.25], [YMid],
								[1.0], [false], 
								[0.0], [relFreq]);
			setRecBoxSettings(	[true], [(XX-1)*dx*0.75], [YMid]);
			break;
		case "Perforated sheet":
			var lambda = dPerf*2;
			var relFreq = (c/lambda)/fs;
			setSrcBoxSettings(	[true], 
								[(XX-1)*dx*0.25], [YMid],
								[1.0], [false], 
								[0.0], [relFreq]);
			setRecBoxSettings(	[true], [(XX-1)*dx*0.75], [YMid]);
			break;
		case "Square object":		// Fall through
		case "Circular object":
			setSrcBoxSettings(	[true], 
								[(XX-1)*dx*0.25], [YMid],
								[1.0], [false], 
								[0.0], [srcFreqDefault[0]]);
			setRecBoxSettings(	[true], [(XX-1)*dx*0.95], [YMid]);
			break;
		case "Sonic crystal":
			var lambda = dx*2*25;		// Because cylinders 25 pixels/grid steps apart
			var relFreq = c/lambda/fs;
			setSrcBoxSettings(	[true], 
								[(XX-1)*dx*0.25], [YMid],
								[1.0], [false], 
								[0.0], [relFreq]);
			setRecBoxSettings(	[true], [(XX-1)*dx*0.95], [YMid]);
			break;
		case "Binary amplitude diffuser":	// Fall through
		case "Schroeder diffuser":
			var lambda = dx*2*5*7;		// Because well depth step size is 5 pixels/grid steps
			var relFreq = c/lambda/fs;
			setSrcBoxSettings(	[true], 
								[(XX-1)*dx*0.5], [YMid],
								[1.0], [false], 
								[0.0], [relFreq]);
			setRecBoxSettings(	[true], [(XX-1)*dx*0.75], [YMid]);
			break;
		case "Barrier":
			setSrcBoxSettings(	[true], 
								[(XX-1)*dx*0.25], [(YY-1)*dx*0.25],
								[1.0], [false], 
								[0.0], [srcFreqDefault[0]]);
			setRecBoxSettings(	[true], [(XX-1)*dx*0.75], [(YY-1)*dx*0.25]);
			break;
		case "Maze":
			setSrcBoxSettings(	[true], 
								[(XX-1)*dx*0.475], [(YY-1)*dx*0.975],
								[1.0], [false], 
								[0.0], [srcFreqDefault[0]]);
			setRecBoxSettings(	[true], [(XX-1)*dx*0.525], [(YY-1)*dx*0.025]);
			//cLimBox.value = cLimDefault*2;
			break;
		case "Squiggle":
			setSrcBoxSettings(	[true, true, true], 
								[(XX-1)*dx*0.4, (XX-1)*dx*0.55, (XX-1)*dx*0.9], 
								[(YY-1)*dx*0.15, (YY-1)*dx*0.85, (YY-1)*dx*0.3],
								[1.0, 1.0, 1.0], [false, false, false], 
								[0.0, 0.8, 1.6], srcFreqDefault.slice(0,3));
			setRecBoxSettings(	[true], [(XX-1)*dx*0.7], [(YY-1)*dx*0.5]);
			//cLimBox.value = cLimDefault*3;
			break;
		case "Hello world":
			setSrcBoxSettings(	[true, true, true, true], 
								[(XX-1)*dx*0.075, (XX-1)*dx*0.85, (XX-1)*dx*0.35, (XX-1)*dx*0.85], 
								[(YY-1)*dx*0.15, (YY-1)*dx*0.8, (YY-1)*dx*0.5, (YY-1)*dx*0.05], 
								[1.0, 1.0, 1.0, 1.0], [false, true, false, true], 
								[0.0, 0.6, 1.2, 1.8], srcFreqDefault.slice(0,4));
			setRecBoxSettings(	[true], [(XX-1)*dx*0.7], [(YY-1)*dx*0.5]);
			//cLimBox.value = cLimDefault*2;
			break;
		default:
			setSrcBoxSettings(	[true],
								[XMid], [YMid],
								[1.0], [false], 
								[0.0], [srcFreqDefault[0]]);
			setRecBoxSettings(	[true], [XMid*1.5], [YMid]);
			break;
	}
	// Source updates
	olSrcSettingsUpdate(false);			// Get active sources etc. (with no resetting/updates)
	olSrcPosCheck(true, true);			// Update positions (doing reset and plot update)
	// Receiver updates
	olRecSettingsUpdate(false);			// Get active receivers etc. (with no resetting/updates)
	olRecPosCheck(true, true);			// Update positions (doing reset and plot update)
	// Reset this to what it was before
	updateOL = currentUpdateOL;
	// Also get real time updates
	rtInputUpdate(true);				// Do RT figure updates
	// Update Python
	//updateButton();					// Don't need full update as done stuff above
	setValues();
	// Update header
	nextHeaderUpdate = mainHeaderPrefix + "Ready!!";
	mainHeader.innerHTML = nextHeaderUpdate;
	// Reset load examples box
	examplesBox.value = -1;
}

// Make source table
function makeSrcTable() {
	printToDebug("Make source table");
	// Initial table number of rows (i.e. headers)
	var initTableSize = srcTable.rows.length;
	// Loop round rows
	for (var i = 0; i<NSrc; i++){
		// Add row
		var rowCount = initTableSize+i;
		var row = srcTable.insertRow(rowCount);
		// Add columns
		// Source number label
		col = 0;
		var cell = row.insertCell(col);
		var iSrc = i+1;
		srcTxt.push("S#"+iSrc.toString());
		cell.innerHTML = srcTxt[i];
		// Active toggle
		col += 1;
		var cell = row.insertCell(col);
		var inputElement = document.createElement("input");
		inputElement.type = "checkbox";
		inputElement.id = "srcActive"+iSrc.toString();
		inputElement.name = "srcActive"+iSrc.toString();
		inputElement.onchange = function(){olSrcSettingsUpdate();};
		inputElement.title = "Source #"+iSrc.toString()+" active";
		cell.appendChild(inputElement);
		srcActiveBox.push(document.getElementById(inputElement.id));
		// Invert toggle
		col += 1;
		var cell = row.insertCell(col);
		var inputElement = document.createElement("input");
		inputElement.type = "checkbox";
		inputElement.id = "srcInv"+iSrc.toString();
		inputElement.name = "srcInv"+iSrc.toString();
		inputElement.onchange = function(){olSrcSettingsUpdate();};
		inputElement.title = "Source #"+iSrc.toString()+" invert";
		cell.appendChild(inputElement);
		srcInvBox.push(document.getElementById(inputElement.id));
		// Amplitude
		col += 1;
		var cell = row.insertCell(col);
		var inputElement = document.createElement("input");
		inputElement.type = "number";
		inputElement.id = "srcAmp"+iSrc.toString();
		inputElement.name = "srcAmp"+iSrc.toString();
		inputElement.min = 0.0;
		inputElement.max = 1.0;
		inputElement.step = 0.01;
		inputElement.value = 1.0;
		inputElement.onchange = function(){constrainInput(this).then(olSrcSettingsUpdate());};
		inputElement.style="width:50px";
		inputElement.title = "Source #"+iSrc.toString()+" amplitude";
		cell.appendChild(inputElement);
		srcAmpBox.push(document.getElementById(inputElement.id));
		// Delay time (ms)
		col += 1;
		var cell = row.insertCell(col);
		var inputElement = document.createElement("input");
		inputElement.type = "number";
		inputElement.id = "srcDelay"+iSrc.toString();
		inputElement.name = "srcDelay"+iSrc.toString();
		inputElement.min = 0.0;
		inputElement.max = 10.0;
		inputElement.step = 0.1;
		inputElement.value = 0.0;
		inputElement.onchange = function(){constrainInput(this).then(olSrcSettingsUpdate());};
		inputElement.style="width:60px";
		inputElement.title = "Source #"+iSrc.toString()+" delay (ms)";
		cell.appendChild(inputElement);
		srcDelayBox.push(document.getElementById(inputElement.id));
		// Source centre frequency (Hz)
		col += 1;
		var cell = row.insertCell(col);
		var inputElement = document.createElement("input");
		inputElement.type = "number";
		inputElement.id = "srcFreq"+iSrc.toString();
		inputElement.name = "srcFreq"+iSrc.toString();
		inputElement.min = 20.0;
		inputElement.max = 1000.0;
		inputElement.step = 1;
		inputElement.value = 500;
		inputElement.onchange = function(){constrainInput(this).then(olSrcSettingsUpdate());};
		inputElement.style="width:70px";
		inputElement.title = "Source #"+iSrc.toString()+" centre frequency (Hz)";
		cell.appendChild(inputElement);
		srcFreqBox.push(document.getElementById(inputElement.id));
		// x coord (m)
		col += 1;
		var cell = row.insertCell(col);
		var inputElement = document.createElement("input");
		inputElement.type = "number";
		inputElement.id = "srcXCoord"+iSrc.toString();
		inputElement.name = "srcXCoord"+iSrc.toString();
		inputElement.min = 0.0;		// These get overwritten based on grid size
		inputElement.max = 10.0;
		inputElement.step = 1.0;
		inputElement.value = 1.0;
		inputElement.onchange = function(){constrainInput(this).then(olSrcPosUpdate());};
		inputElement.style="width:60px";
		inputElement.title = "Source #"+iSrc.toString()+" x coordinate (m)";
		cell.appendChild(inputElement);
		srcXBox.push(document.getElementById(inputElement.id));
		// y coord (m)
		col += 1;
		var cell = row.insertCell(col);
		var inputElement = document.createElement("input");
		inputElement.type = "number";
		inputElement.id = "srcYCoord"+iSrc.toString();
		inputElement.name = "srcYCoord"+iSrc.toString();
		inputElement.min = 0.0;		// These get overwritten based on grid size
		inputElement.max = 10.0;
		inputElement.step = 1.0;
		inputElement.value = 1.0;
		inputElement.onchange = function(){constrainInput(this).then(olSrcPosUpdate());};
		inputElement.style="width:60px";
		inputElement.title = "Source #"+iSrc.toString()+" y coordinate (m)";
		cell.appendChild(inputElement);
		srcYBox.push(document.getElementById(inputElement.id));
	}
	// Set first source to active
	//srcActiveBox[0].checked = true;
}

// Make receiver table
function makeRecTable() {
	printToDebug("Make receiver table");
	// Initial table number of rows (i.e. headers)
	var initTableSize = recTable.rows.length;
	// Loop round rows
	for (var i = 0; i<NRec; i++){
		// Add row
		var rowCount = initTableSize+i;
		var row = recTable.insertRow(rowCount);
		// Add columns
		// Receiver number label
		col = 0;
		var cell = row.insertCell(col);
		var iRec = i+1;
		recTxt.push("R#"+iRec.toString());
		cell.innerHTML = recTxt[i];
		// Active toggle
		col += 1;
		var cell = row.insertCell(col);
		var inputElement = document.createElement("input");
		inputElement.type = "checkbox";
		inputElement.id = "recActive"+iRec.toString();
		inputElement.name = "recActive"+iRec.toString();
		inputElement.onchange = function(){olRecSettingsUpdate();};
		inputElement.title = "Receiver #"+iRec.toString()+" active";
		if (NRec == 1) { inputElement.style = "display:none"; }					// Note: active toggle hidden if only one
		cell.appendChild(inputElement);
		recActiveBox.push(document.getElementById(inputElement.id));
		// Skip columns															// Note: skip columns that don't apply to receivers
		for (var j = 0; j < 4; j++) {
			col += 1;
			row.insertCell(col);
		}
		// x coord (m)
		col += 1;
		var cell = row.insertCell(col);
		var inputElement = document.createElement("input");
		inputElement.type = "number";
		inputElement.id = "recXCoord"+iRec.toString();
		inputElement.name = "recXCoord"+iRec.toString();
		inputElement.min = 0.0;		// These get overwritten based on grid size
		inputElement.max = 10.0;
		inputElement.step = 1.0;
		inputElement.value = 1.0;
		inputElement.onchange = function(){constrainInput(this).then(olRecPosUpdate());};
		inputElement.style="width:60px";
		inputElement.title = "Receiver #"+iRec.toString()+" x coordinate (m)";
		cell.appendChild(inputElement);
		recXBox.push(document.getElementById(inputElement.id));
		// y coord (m)
		col += 1;
		var cell = row.insertCell(col);
		var inputElement = document.createElement("input");
		inputElement.type = "number";
		inputElement.id = "recYCoord"+iRec.toString();
		inputElement.name = "recYCoord"+iRec.toString();
		inputElement.min = 0.0;		// These get overwritten based on grid size
		inputElement.max = 10.0;
		inputElement.step = 1.0;
		inputElement.value = 1.0;
		inputElement.onchange = function(){constrainInput(this).then(olRecPosUpdate());};
		inputElement.style="width:60px";
		inputElement.title = "Receiver #"+iRec.toString()+" y coordinate (m)";
		cell.appendChild(inputElement);
		recYBox.push(document.getElementById(inputElement.id));
	}
	// Set first source to active
	//recActiveBox[0].checked = true;
}

// Get linspace x and y values for 2D mesh
function getXYValues() {
	printToDebug("Get x-y values");
	// Get linspace x and y values
	xValues = linspace(0,X*Nx,Nx,false)
	yValues = linspace(0,X*Ny,Ny,false)
}

// Makes initial figure
function makeFig() {
	printToDebug("Make figure");
	// Get colour scale, x-y values, and plot size
	getColorScale();
	getGreyScale();
	getXYValues();
	getPlotSize();
	// Set data
	var dataFDTD = {
		z: pyZValues,
		x: xValues,
		y: yValues,
		type: 'heatmap',
		zsmooth: 'fast',
		colorscale: colorscaleValue,
		colorbar: {
			len: 1,
			outlinewidth: 2,
			tickfont: {size: 12},
		},	// Also has x property for how far left/right
		zmin: -cLim,
		zmax: cLim,
	};
	var dataMesh = {
		z: gsArray,
		x: xValues,
		y: yValues,
		type: 'heatmap',
		//zsmooth: 'best',
		zsmooth: false,
		//colorscale: 'Greys',
		colorscale: colorscaleGrey,
		showscale: false,			// No colorbar
		visible: meshShowStatus,	// If shown/hidden
		zmin: 0,
		zmax: 1,
	};
	var dataSrc = {
		x: whereIsTrue(srcX, srcActive),
		y: whereIsTrue(srcY, srcActive),
		mode: 'markers+text',
		opacity: 0.75,
		type: 'scatter',
		name: 'Source location',
		text: whereIsTrue(srcTxt, srcActive),
		textposition: 'top right',
		visible: srcShowStatus,		// If shown/hidden
		marker: { 
			size: 12, 
			color: 'rgb(200, 200, 200)',
			line: {
				color: 'rgb(50, 50, 50)',
				width: 4
				}
			}
	};
	var dataRec = {
		x: whereIsTrue(recX, recActive),
		y: whereIsTrue(recY, recActive),
		mode: 'markers+text',
		opacity: 0.75,
		type: 'scatter',
		name: 'Receiver location',
		text: whereIsTrue(recTxt, recActive),
		textposition: 'top right',
		visible: recShowStatus,		// If shown/hidden
		marker: { 
			size: 12, 
			color: 'rgb(200, 200, 200)',
			line: {
				color: 'rgb(50, 50, 50)',
				width: 4
				}
			}
	};
	// Data input
	data = [];
	data[fdtdFigLayer] = dataFDTD;
	data[meshFigLayer] = dataMesh;
	data[srcFigLayer] = dataSrc;
	data[recFigLayer] = dataRec;
	// Define layout
	var layout = {
		autosize: false,
		width: plotWidth,	// For manual sizing as aspect ratio doesn't work
		height: plotHeight,
		plot_bgcolor: bgColour,
		margin: {
			l: 40,
			r: 10,
			b: 40,
			t: 10,
			pad: 0
		},
		showlegend: false,
		//scene: {aspectratio: {'x':1, 'y':1}},
		//scene: {aspectmode: "data"},
		/*images: [{
			x: 0,
			y: 0,
			sizex: Dx,
			sizey: Dy,
			source: imageFile.src,
			xanchor: "left",
			yanchor: "bottom",
			xref: "x",
			yref: "y",
			//opacity: 0.3
			layer: "below"
		}],*/
		xaxis: {
			range: [xValues[0], xValues[Nx-1]],
			showline: true,
			mirror: true,
			showgrid: false,
			zeroline: false,
			linewidth: 2,
			tickwidth: 2,
			ticks: "inside",
			tickfont: {size: 14},
		},
		yaxis: {
			range: [yValues[0], yValues[Ny-1]],
			showline: true,
			mirror: true,
			showgrid: false,
			zeroline: false,
			linewidth: 2,
			tickwidth: 2,
			ticks: "inside",
			tickfont: {size: 14},
		},
		modebar: {orientation: 'v'}
	};
	/*var layout = [
	{
		xaxis: {
			automargin: true,
			scaleanchor: 'y',
			scaleratio: 1,
		},
		yaxis: {
			automargin: true,
			scaleanchor: 'x',
			scaleratio: 1,
		}
	}
	];*/
	// Config - see:
	// https://plotly.com/javascript/configuration-options/?_ga=2.131771919.1025833578.1689411173-1503907169.1683466811#edit-mode
	// https://github.com/plotly/plotly.js/blob/master/src/plot_api/plot_config.js
	// https://github.com/plotly/plotly.js/blob/master/src/components/modebar/buttons.js
	// https://github.com/plotly/plotly.js/blob/master/src/fonts/ploticon.js
	var renderButton = {
		name: 'Save current view',
		icon: {
			width: 500,
			height: 500,
			path: "M64 32C28.7 32 0 60.7 0 96V288 448c0 17.7 14.3 32 32 32s32-14.3 32-32V320h95.3L261.8 466.4c10.1 14.5 30.1 18 44.6 7.9s18-30.1 7.9-44.6L230.1 309.5C282.8 288.1 320 236.4 320 176c0-79.5-64.5-144-144-144H64zM176 256H64V96H176c44.2 0 80 35.8 80 80s-35.8 80-80 80z"
		},
		click: function(gd) { renderImageButton(); }
	}
	var loadButton = {
		name: 'Load file',
		icon: {
			width: 500,
			height: 500,
			path: "M384 480h48c11.4 0 21.9-6 27.6-15.9l112-192c5.8-9.9 5.8-22.1 .1-32.1S555.5 224 544 224H144c-11.4 0-21.9 6-27.6 15.9L48 357.1V96c0-8.8 7.2-16 16-16H181.5c4.2 0 8.3 1.7 11.3 4.7l26.5 26.5c21 21 49.5 32.8 79.2 32.8H416c8.8 0 16 7.2 16 16v32h48V160c0-35.3-28.7-64-64-64H298.5c-17 0-33.3-6.7-45.3-18.7L226.7 50.7c-12-12-28.3-18.7-45.3-18.7H64C28.7 32 0 60.7 0 96V416c0 35.3 28.7 64 64 64H87.7 384z"
		},
		click: function(gd) { loadFileBox.click(); }
	}
	var clearButton = {
		name: 'Clear all',
		icon: {
			width: 500,
			height: 500,
			path: "M48.5 224H40c-13.3 0-24-10.7-24-24V72c0-9.7 5.8-18.5 14.8-22.2s19.3-1.7 26.2 5.2L98.6 96.6c87.6-86.5 228.7-86.2 315.8 1c87.5 87.5 87.5 229.3 0 316.8s-229.3 87.5-316.8 0c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0c62.5 62.5 163.8 62.5 226.3 0s62.5-163.8 0-226.3c-62.2-62.2-162.7-62.5-225.3-1L185 183c6.9 6.9 8.9 17.2 5.2 26.2s-12.5 14.8-22.2 14.8H48.5z"
		},
		click: function(gd) { meshResetButton(); }
	}
	var config = {
		modeBarButtons: [[loadButton,clearButton,renderButton],['pan2d','zoom2d','zoomIn2d','zoomOut2d','resetScale2d','toImage'],
						['drawline','drawopenpath','drawrect','drawcircle','eraseshape']],
		displayModeBar: true,//altModebarDiv==null,
		toImageButtonOptions: { filename: imageSaveName },
		//modeBarStyle: {orientation: 'v'}
		/*modeBarButtonsToAdd: ['drawline','drawopenpath','drawrect','drawcircle','eraseshape',
							{
								name: 'Render image',
								icon: {
									width: 857.1,
									height: 1000,
									path: "M64 32C28.7 32 0 60.7 0 96V288 448c0 17.7 14.3 32 32 32s32-14.3 32-32V320h95.3L261.8 466.4c10.1 14.5 30.1 18 44.6 7.9s18-30.1 7.9-44.6L230.1 309.5C282.8 288.1 320 236.4 320 176c0-79.5-64.5-144-144-144H64zM176 256H64V96H176c44.2 0 80 35.8 80 80s-35.8 80-80 80z"},
								click: function(gd) { renderImageButton(); }
							}],
		modeBarButtonsToRemove: ['zoom2d','select2d','lasso2d','autoScale2d']*/
		//editable: true
	};
	// Clear div of HTML
	plotDiv.innerHTML = '';
	// Make new plot
	Plotly.newPlot(plotDivId, data, layout, config);
	// If alternative modebar div exists
	if (altModebarDiv!=null) {
		if (!figExists) {
			// Make alternative buttons if first time made fig
			var modebarDataTitles = [];
			modebarDataTitles.push(loadButton['name']);
			modebarDataTitles.push(renderButton['name']);
			modebarDataTitles.push(clearButton['name']);
			modebarDataTitles.push(...["Erase active shape", "Draw line", "Draw open freeform", "Draw rectangle", "Draw circle"]);
			modebarDataTitles.push(...["Pan", "Zoom", "Zoom in", "Zoom out", "Reset axes", "Download plot as a png"]);
			var modebarTitles = modebarDataTitles;
			makeAlternativeModebarButtons(altModebarDiv, modebarDataTitles, modebarTitles);
		}
		// Hide modebar (different to displayModeBar=false in config, which means there is no modebar)
		var modebarContainer = plotDiv.getElementsByClassName("modebar-container");
		//modebarContainer[0].hidden = true;
		modebarContainer[0].style.display = "none";
		// Click button want to start with (i.e. Zoom)
		var btn = document.getElementById("modebarBtn9");
		btn.click();
		btn.focus();
	}
	// Figure now exists
	figExists = true;
}

// Update figure data and layout
function updateFig(updateData, updataLayout, ind=0) {
	printToDebug("Update figure data and layout");
	Plotly.update(plotDivId, updateData, updataLayout, ind);
}

// Update figure data
function updateFigData(update, ind=0) {
	printToDebug("Update figure data");
	Plotly.restyle(plotDivId, update, ind);
}

// Update figure layout
function updateFigLayout(update={}, getDimsFromPlot=false) {
	printToDebug("Update figure layout");
	// Include update of plot size
	getPlotSize(getDimsFromPlot)
	update['width'] = plotWidth;
	update['height'] = plotHeight;
	// Update layout
	Plotly.relayout(plotDivId, update);
}

// Get modebar element from data title
function getModebarElement(modebarDataTitle) {
	var modebarElements = plotDiv.getElementsByClassName("modebar-btn");
	for (var i = 0; i<modebarElements.length; i++) {
		if (modebarElements[i].getAttribute("data-title") == modebarDataTitle) {
			return modebarElements[i];
		}
	}
}

// Make alternative buttons to trigger modebar options
function makeAlternativeModebarButtons(divId, modebarDataTitles, title, iActive) {
	// Number of buttons to make
	var NButton = modebarDataTitles.length
	// Text/html to use
	let html = modebarDataTitles;
	// Loop and add
	for (var i=0 ; i<NButton ; i++) {
		// Add break if already button above
		//if (i>0) { divId.appendChild(document.createElement("br")); }
		// Get element to trigger
		let modebarElement = getModebarElement(modebarDataTitles[i]);
		let debugTxt = "Modebar button click: "+html[i];
		// Make button
		var el = document.createElement("button");
		if (html[i] in svgHtml) {
			el.innerHTML += svgHtml[html[i]];
			el.getElementsByTagName('svg')[0].setAttribute("width", "75%");
			el.getElementsByTagName('svg')[0].setAttribute("height", "75%");
		}
		else { el.innerHTML += html[i]; }
		el.id = "modebarBtn"+i.toString();
		el.name = "modebarBtn"+i.toString();
		el.classList.add("modebar-buttons");
		if (html[i] == "Pan") {
			el.onclick = function() {
				printToDebug(debugTxt);
				modebarElement.click();
				updateFigLayout();	// Extra layout update to fix aspect ratio
			};
		}
		else {
			el.onclick = function() {
				printToDebug(debugTxt);
				modebarElement.click();
			};
		}
		el.title = title[i];
		divId.appendChild(el);
	}
}

// Update plot size - triggered by window resizing
function onWindowResize(e) {
	// Get size to make plot
	getPlotSize()
	// Update layout
	var layoutUpdate = {	width: plotWidth,
							height: plotHeight };
	updateFigLayout(layoutUpdate);
}

// Snap coordinate to discretised FDTD grid
function snapToGrid(x, X) {
	return Math.round(x/X)*X
}

// Get axes range from current plot, including estimate of No. of pixels
function getRangeFromPlot() {
	var xRangePlot = plotDiv.layout.xaxis.range;
	var yRangePlot = plotDiv.layout.yaxis.range;
	//var XPlot = fdtdObj.X;	// Prev.
	var XPlot = X;				// Current
	xRangePlot[0] = snapToGrid(xRangePlot[0], XPlot)
	xRangePlot[1] = snapToGrid(xRangePlot[1], XPlot)
	yRangePlot[0] = snapToGrid(yRangePlot[0], XPlot)
	yRangePlot[1] = snapToGrid(yRangePlot[1], XPlot)
	var xExtent = xRangePlot[1]-xRangePlot[0];
	var yExtent = yRangePlot[1]-yRangePlot[0];
	var NxPlot = Math.round(xExtent/XPlot)+1;
	var NyPlot = Math.round(yExtent/XPlot)+1;
	return [xRangePlot, yRangePlot, NxPlot, NyPlot];
}

// Get size to make plot
function getPlotSize(getDimsFromPlot=false) {
	printToDebug("Get plot size");
	// Size of plot div/window
	plotWidth = Math.min(plotDiv.offsetWidth, window.innerWidth);
	plotHeight = window.innerHeight;
	// Max proportion of window want to use
	plotWidth *= plotWidthRelToWindow;
	plotHeight *= plotHeightRelToWindow;
	// Fudge to take in to account colorbar and padding
	var wPad = 40+10+120;
	var hPad = 40+10;
	plotWidth -= wPad;
	plotHeight -= hPad;
	// Size of plot area
	if (getDimsFromPlot) {
		var vals = getRangeFromPlot();
		var NxPlot = vals[2];
		var NyPlot = vals[3];
	} else {
		// Just use current values
		var NxPlot = Nx;
		var NyPlot = Ny;
	}
	// Size relative to plot dimensions
	var relPlotWidth = plotWidth/NxPlot;
	var relPlotHeight = plotHeight/NyPlot;
	var relPlotMin = Math.min(relPlotWidth, relPlotHeight);
	// Size to make plot
	plotWidth = Math.round(NxPlot*relPlotMin+wPad);
	plotHeight = Math.round(NyPlot*relPlotMin+hPad);
}

// Reset simulation, including redraw of figure
function resetAll(doMakeFig=true) {
	printToDebug("Reset all");
	// Sim time is zero
	tSimDivUpdate(0.0);
	// Set running to false
	fdtdObj.running = false;
	// Reset sim (includes reset of pressures and update of source functions)
	fdtdObj.runReset();
	// p data Request (should be all zeros)
	pyPRequest();
	// If this is first time then reset mesh
	if (initialising) { initialising = false; resetMesh(); };
	// Make figure
	if (doMakeFig) { makeFig(); };
	// Let know we're done
	nextHeaderUpdate = mainHeaderPrefix + "Ready!!";		// Clunky fix for now
	mainHeader.innerHTML = nextHeaderUpdate;
}

// Trigger update via input box
function thresholdSliderUpdate() {
	imThreshBox.value = imThreshSlider.value;
	var onChangeEvent = new Event('change');
	imThreshBox.dispatchEvent(onChangeEvent);
}

// Update offline plot update status
function olPlotUpdateStatus() {
	printToDebug("Offline plot update status");
	// Get status
	updateOL = OLUpdateBox.checked;
}

// Update mesh check status
function olMeshCheckStatus() {
	printToDebug("Offline mesh check status");
	// Get status
	checkAndFixMesh = OLMeshCheckBox.checked;
}

// Do downloads status
function olDownloadsStatus() {
	printToDebug("Offline do downloads status");
	// Get status
	gifDownload = downloadGifBox.checked;
	wavDownload = downloadWavBox.checked;
}

// Check source position and then trigger update (locally)
function olSrcPosCheck(doResetOnOLUpdate=true, doPlotOnOLUpdate=true) {
	printToDebug("Offline source position check");
	// Check all sources
	for (var i = 0; i<NSrc; i++) {
		var xCoord = Number(srcXBox[i].value);
		var yCoord = Number(srcYBox[i].value);
		if ( xCoord < 0 || xCoord > Dx ) {
			srcXBox[i].value = Math.round(Dx*srcXRel[i]/srcStep)*srcStep;
		}
		if ( yCoord < 0 || yCoord > Dx ) {
			srcYBox[i].value = Math.round(Dy*srcYRel[i]/srcStep)*srcStep;
		}
	}
	olSrcPosUpdate(doResetOnOLUpdate, doPlotOnOLUpdate)
}

// Check receiver position and then trigger update (locally)
function olRecPosCheck(doResetOnOLUpdate=true, doPlotOnOLUpdate=true) {
	printToDebug("Offline receiver position check");
	// Check all receivers
	for (var i = 0; i<NRec; i++) {
		var xCoord = Number(recXBox[i].value);
		var yCoord = Number(recYBox[i].value);
		if ( xCoord < 0 || xCoord > Dx ) {
			recXBox[i].value = Math.round(Dx*recXRel[i]/recStep)*recStep;
		}
		if ( yCoord < 0 || yCoord > Dx ) {
			recYBox[i].value = Math.round(Dy*recYRel[i]/recStep)*recStep;
		}
	}
	olRecPosUpdate(doResetOnOLUpdate, doPlotOnOLUpdate)
}

// Updates source location parameters (locally)
function olSrcPosUpdate(doResetOnOLUpdate=true, doPlotOnOLUpdate=true) {
	printToDebug("Offline source position update");
	// Get source position(s) and check if changed
	var srcChanged = false;
	for (var i = 0; i<NSrc; i++) {
		var newX = Number(srcXBox[i].value);
		var newY = Number(srcYBox[i].value);
		if (srcX[i] != newX) {
			srcChanged = true;
			srcX[i] = newX;
		}
		if (srcY[i] != newY) {
			srcChanged = true;
			srcY[i] = newY;
		}
		// Relative source position(s)
		srcXRel[i] = srcX[i]/Dx;
		srcYRel[i] = srcY[i]/Dy;
	}
	// Quick fudge fix - because sources can also have changed if active or not when loading examples, so just always update
	srcChanged = true;
	// If not running (i.e. offline)
	if (!fdtdObj.running && updateOL) {
		// If doing offline reset
		if (resetOnOLUpdate && doResetOnOLUpdate) {
			// Reset (which will cause update of parameters on next sim start)
			resetAll(doMakeFig=false);
		}
		// If doing offline plot update
		if (figExists && doPlotOnOLUpdate) {
			// Update source plot if needed (only plot active sources)
			if (srcChanged) {
				var update = {	'x': 	[whereIsTrue(srcX, srcActive)], 
								'y': 	[whereIsTrue(srcY, srcActive)],
								'text': [whereIsTrue(srcTxt, srcActive)]};
				updateFigData(update, srcFigLayer);
			}
		}
	}
}

// Updates receivers location parameters (locally)
function olRecPosUpdate(doResetOnOLUpdate=true, doPlotOnOLUpdate=true) {
	printToDebug("Offline receiver position update");
	// Get receiver position(s) and check if changed
	var recChanged = false;
	for (var i = 0; i<NRec; i++) {
		var newX = Number(recXBox[i].value);
		var newY = Number(recYBox[i].value);
		if (recX[i] != newX) {
			recChanged = true;
			recX[i] = newX;
		}
		if (recY[i] != newY) {
			recChanged = true;
			recY[i] = newY;
		}
		// Relative receiver position(s)
		recXRel[i] = recX[i]/Dx;
		recYRel[i] = recY[i]/Dy;
	}
	// Quick fudge fix - because receivers can also have changed if active or not when loading examples, so just always update
	recChanged = true;
	// If not running (i.e. offline)
	if (!fdtdObj.running && updateOL) {
		// If doing offline reset
		if (resetOnOLUpdate && doResetOnOLUpdate) {
			// Reset (which will cause update of parameters on next sim start)
			resetAll(doMakeFig=false);
		}
		// If doing offline plot update
		if (figExists && doPlotOnOLUpdate) {
			// Update source plot if needed (only plot active sources)
			if (recChanged) {
				var update = {	'x': 	[whereIsTrue(recX, recActive)], 
								'y': 	[whereIsTrue(recY, recActive)],
								'text': [whereIsTrue(recTxt, recActive)]};
				updateFigData(update, recFigLayer);
			}
		}
	}
}

// Source type setting (all sources)
function olSrcTypeAllUpdate() {
	printToDebug("Source type (all) update");
	// Get source type
	var srcTypeAll = srcTypeAllBox.options[srcTypeAllBox.selectedIndex].text;
	var srcPeriodsAll = Number(srcPeriodsAllBox.value);
	if (srcTypeAll == "Tone pulse") {
		srcTypeAll += " "+srcPeriodsAll.toString();
	}
	// Assign to all
	for (var i = 0; i<NSrc; i++) {
		srcType[i] = srcTypeAll;
	}
}

// Source settings (active, amp, invert, delay) update
function olSrcSettingsUpdate(doResetOnOLUpdate=true) {
	printToDebug("Source settings update");
	// Set plotting to same as reset (as generally want to do the same thing)
	var doPlotOnOLUpdate = doResetOnOLUpdate;
	// Get source settings and check if changed active status
	var srcChanged = false;
	for (var i = 0; i<NSrc; i++) {
		var isActive = srcActiveBox[i].checked;
		if (srcActive[i] != isActive) {
			srcChanged = true;
			srcActive[i] = isActive;
		}
		srcAmp[i] = Number(srcAmpBox[i].value);
		srcInv[i] = srcInvBox[i].checked;
		srcDelay[i] = Number(srcDelayBox[i].value);
		srcFreq[i] = Number(srcFreqBox[i].value);
	}
	// If not running (i.e. offline)
	if (!fdtdObj.running  && updateOL) {
		// If doing offline reset
		if (resetOnOLUpdate && doResetOnOLUpdate) {
			// Reset (which will cause update of parameters on next sim start)
			resetAll(doMakeFig=false);
		}
		// If doing offline plot update
		if (figExists  && doPlotOnOLUpdate) {
			// Update source plot if needed (only plot active sources)
			if (srcChanged) {
				var update = {	'x': 	[whereIsTrue(srcX, srcActive)], 
								'y': 	[whereIsTrue(srcY, srcActive)],
								'text': [whereIsTrue(srcTxt, srcActive)]};
				updateFigData(update, srcFigLayer);
			}
		}
	}
}

// Receiver settings (active) update
function olRecSettingsUpdate(doResetOnOLUpdate=true) {
	printToDebug("Receiver settings update");
	// Set plotting to same as reset (as generally want to do the same thing)
	var doPlotOnOLUpdate = doResetOnOLUpdate;
	// Get receiver settings and check if changed active status
	var recChanged = false;
	for (var i = 0; i<NRec; i++) {
		var isActive = recActiveBox[i].checked;
		if (recActive[i] != isActive) {
			recChanged = true;
			recActive[i] = isActive;
		}
	}
	// If not running (i.e. offline)
	if (!fdtdObj.running  && updateOL) {
		// If doing offline reset
		if (resetOnOLUpdate && doResetOnOLUpdate) {
			// Reset (which will cause update of parameters on next sim start)
			resetAll(doMakeFig=false);
		}
		// If doing offline plot update
		if (figExists  && doPlotOnOLUpdate) {
			// Update source plot if needed (only plot active sources)
			if (recChanged) {
				var update = {	'x': 	[whereIsTrue(recX, recActive)], 
								'y': 	[whereIsTrue(recY, recActive)],
								'text': [whereIsTrue(recTxt, recActive)]};
				updateFigData(update, recFigLayer);
			}
		}
	}
}

// Updates grid size parameters (locally)
function olGridSizeUpdate(doResetOnOLUpdate=true, doMeshUpdate=false) {
	printToDebug("Offline grid size update");
	// Set plotting to same as reset (as generally want to do the same thing)
	var doPlotOnOLUpdate = doResetOnOLUpdate;
	// Get values
	Nx = Number(XGridBox.value);
	Ny = Number(YGridBox.value);
	X = Number(gridSpacingBox.value)*1e-3;
	Dx = (Nx-1)*X;
	Dy = (Ny-1)*X;
	// Update frequency box limits
	setFreqBoxLims();
	// Update source/receievr adjustment parameters
	srcStep = 10**Math.round(Math.log10(X));
	for (var i = 0; i<NSrc; i++) {
		srcXBox[i].max = Math.round(Dx/srcStep)*srcStep;
		srcYBox[i].max = Math.round(Dy/srcStep)*srcStep;
		srcXBox[i].step = srcStep;
		srcYBox[i].step = srcStep;
	}
	recStep = srcStep;
	for (var i = 0; i<NRec; i++) {
		recXBox[i].max = Math.round(Dx/recStep)*recStep;
		recYBox[i].max = Math.round(Dy/recStep)*recStep;
		recXBox[i].step = recStep;
		recYBox[i].step = recStep;
	}
	// Update plot if not running (i.e. offline)
	if (!fdtdObj.running && updateOL) {
		// If doing offline reset
		if (resetOnOLUpdate && doResetOnOLUpdate) {
			// Reset (which will cause update of parameters on next sim start)
			resetAll(doMakeFig=false);
		}
		// If doing offline plot update
		if (figExists && doPlotOnOLUpdate) {
			// Get new x and y vectors
			getXYValues()
			// Make empty p value array
			pyZValues = Array(Ny).fill().map(() => Array(Nx).fill(0));
			// make updates
			var dataUpdate = {'x': [xValues], 'y': [yValues], 'z': [pyZValues]};
			var layoutUpdate = { xaxis: plotDiv.layout.xaxis, yaxis: plotDiv.layout.yaxis };	// Copy first (otherwise lose other axis properties)
			layoutUpdate['xaxis']['range'] = [xValues[0], xValues[Nx-1]];
			layoutUpdate['yaxis']['range'] = [yValues[0], yValues[Ny-1]];
			
			// Update sim (leave mesh untouched, including x and y values)
			updateFigData(dataUpdate, fdtdFigLayer);
			// Update mesh if requested
			if (doMeshUpdate) { updateFigData({'x': [xValues], 'y': [yValues]}, meshFigLayer); }
			// Update layout
			updateFigLayout(layoutUpdate);
			
			//updateFig(dataUpdate, layoutUpdate, [fdtdFigLayer, meshFigLayer]);	// Update all - NOT WORKING???
		}
	}
	// Source and receiver check (move if no longer on grid)
	olSrcPosCheck(false, doPlotOnOLUpdate)								// false to avoid multiple resets
	olRecPosCheck(false, doPlotOnOLUpdate)								// false to avoid multiple resets
}

// Update grid step parameters (locally)
function olGridStepUpdate(doResetOnOLUpdate=true) {
	printToDebug("Offline grid step update");
	c = Number(soundSpeedBox.value);
	t = Number(simTimeBox.value)*1e-3;
	// Update frequency box limits
	setFreqBoxLims();
	// If not running (i.e. offline)
	if (!fdtdObj.running) {
		// If doing offline reset
		if (resetOnOLUpdate && doResetOnOLUpdate) {
			// Reset (which will cause update of parameters on next sim start)
			resetAll(doMakeFig=false);
		}
	}
}

// Update mesh parameters (locally)
function olMeshSettingsUpdate(doResetOnOLUpdate=true) {
	printToDebug("Offline mesh settings update");
	// Set plotting to same as reset (as generally want to do the same thing)
	var doPlotOnOLUpdate = doResetOnOLUpdate;
	// New threshold and mode
	var newImThresh = Number(imThreshBox.value);
	var newMode = betaModeBox.value;
	// Check if either have changed
	var threshChanged = false;
	if (newImThresh != imageThreshold) {
		threshChanged = true;
		imageThreshold = newImThresh;
		imThreshSlider.value = imageThreshold;	// Triggered by box so update slider
	}
	var modeChanged = false;
	if (newMode != betaMode) {
		modeChanged = true;
		betaMode = newMode;
	}
	beta = Number(betaBox.value);
	betaBorder = Number(betaBorderBox.value);
	// If not running (i.e. offline)
	if (!fdtdObj.running && updateOL) {
		// If doing offline reset
		if (resetOnOLUpdate && doResetOnOLUpdate) {
			// Reset (which will cause update of parameters on next sim start)
			resetAll(doMakeFig=false);
		}
		// If doing offline plot update
		if (figExists && doPlotOnOLUpdate) {
			// Update to values if threshold or mode has changed
			if (threshChanged || modeChanged) {
				imReplyResetPlot = false;	// Don't remake plot, just update
				setMeshValues();
			}
		}
	}
}

// Update all offline parameters (locally)
function olInputUpdate(doResetOnOLUpdate=false) {
	printToDebug("Offline input(s) update");
	// Run at start so have values in memory
	olPlotUpdateStatus();							// Get status
	olMeshCheckStatus();							// Get status
	olDownloadsStatus();							// Get status
	olGridSizeUpdate(doResetOnOLUpdate);			// Also updates source and receiver position variables
	olSrcSettingsUpdate(false);						// ... false to avoid multiple resets; Source settings other than position
	olRecSettingsUpdate(false);						// ... false to avoid multiple resets; Receiver settings other than position
	olGridStepUpdate(false);						// ... false to avoid multiple resets
	olMeshSettingsUpdate(false);					// ... false to avoid multiple resets
}

// Update real time colour parameters and update figure (whether running or not)
async function rtColourUpdate(doFigUpdate=true) {
	printToDebug("Real time input(s) update");
	cn[0] = Number(cnrBox.value);
	cn[1] = Number(cngBox.value);
	cn[2] = Number(cnbBox.value);
	cz[0] = Number(czrBox.value);
	cz[1] = Number(czgBox.value);
	cz[2] = Number(czbBox.value);
	cp[0] = Number(cprBox.value);
	cp[1] = Number(cpgBox.value);
	cp[2] = Number(cpbBox.value);
	cLim = Number(cLimBox.value);
	getColorScale();
	if (figExists && doFigUpdate) {
		var update = {};
		update['colorscale'] = [colorscaleValue];
		update['zmin'] = -cLim;
		update['zmax'] = cLim;
		updateFigData(update, fdtdFigLayer);
		updateFigLayout({plot_bgcolor: bgColour});
		//await sleep(plotSleepTime);
	};
}

// Update real time plot update rate (whether running or not)
async function rtPlotRateUpdate() {
	printToDebug("Real time plot rate update update");
	plotIthUpdate = Number(plotStepBox.value);
}

// Update real time show/hide mesh (whether running or not)
async function rtMeshShowStatus(doFigUpdate=true) {
	printToDebug("Real time mesh show/hide update");
	meshShowStatus = meshShowBox.checked;
	if (figExists && doFigUpdate) {
		var update = { visible: meshShowStatus };
		updateFigData(update, meshFigLayer);
		//await sleep(plotSleepTime);
	};
}

// Update real time show/hide source(s) (whether running or not)
async function rtSrcShowStatus(doFigUpdate=true) {
	printToDebug("Real time source show/hide update");
	srcShowStatus = srcShowBox.checked;
	if (figExists && doFigUpdate) {
		var update = { visible: srcShowStatus };
		updateFigData(update, srcFigLayer);
		//await sleep(plotSleepTime);
	};
}

// Update real time show/hide receiver(s) (whether running or not)
async function rtRecShowStatus(doFigUpdate=true) {
	printToDebug("Real time receiver show/hide update");
	recShowStatus = recShowBox.checked;
	if (figExists && doFigUpdate) {
		var update = { visible: recShowStatus };
		updateFigData(update, recFigLayer);
		//await sleep(plotSleepTime);
	};
}

// Update real time mesh colour invert (whether running or not)
async function rtMeshColInvStatus(doFigUpdate=true) {
	printToDebug("Real time mesh colour invert update");
	meshColInvStatus = meshColInvBox.checked;
	if (figExists && doFigUpdate) {
		// TODO
		getGreyScale();
		var update = {};
		update['colorscale'] = [colorscaleGrey];
		updateFigData(update, meshFigLayer);
		//await sleep(plotSleepTime);
	};
}

// Reset to default colours
async function rtResetColorScale() {
	printToDebug("Reset colour scale");
	// Set boxes to defaults
	cnrBox.value = cnDefault[0];
	cngBox.value = cnDefault[1];
	cnbBox.value = cnDefault[2];
	czrBox.value = czDefault[0];
	czgBox.value = czDefault[1];
	czbBox.value = czDefault[2];
	cprBox.value = cpDefault[0];
	cpgBox.value = cpDefault[1];
	cpbBox.value = cpDefault[2];
}

// Reset to default colours
async function rtRandomColorScale() {
	printToDebug("Random colour scale");
	// Set boxes to random values
	cnrBox.value = getRandomInt(256);
	cngBox.value = getRandomInt(256);
	cnbBox.value = getRandomInt(256);
	czrBox.value = getRandomInt(256);
	czgBox.value = getRandomInt(256);
	czbBox.value = getRandomInt(256);
	cprBox.value = getRandomInt(256);
	cpgBox.value = getRandomInt(256);
	cpbBox.value = getRandomInt(256);
}

// Update all real-time parameters
function rtInputUpdate(doFigUpdate=false) {
	printToDebug("Real time input(s) update");
	rtResetColorScale();
	rtPlotRateUpdate();
	rtColourUpdate(doFigUpdate);
	rtMeshColInvStatus(doFigUpdate);
	rtMeshShowStatus(doFigUpdate);
	rtSrcShowStatus(doFigUpdate);
	rtRecShowStatus(doFigUpdate);
}

// Set all values in simulation using current locally stored parameters (and then reset)
function setValues() {
	printToDebug("Update fdtd inputs");
	// Update Python values (with offline local values)
	// (Note: x and y opposite way around)
	fdtdObj.c = c;
	fdtdObj.t = t;
	fdtdObj.X = X;
	pyAttRequest(Ny, 'Nxyz', 0);
	pyAttRequest(Nx, 'Nxyz', 1);
	// Ensure all affeceted inputs are up-to-date
	fdtdObj.setInputs();
	// Update sources
	for (var i = 0; i<NSrc; i++){
		// Move or add a source
		if (i < fdtdObj.srcN) { pySrcMove(srcY[i], srcX[i], i);	
		} else {	pySrcAdd(srcY[i], srcX[i]); }
		// Update settings
		var srcA = srcAmp[i];							// Amplitude
		srcA *= ( srcActive[i] === true ? 1 : 0 );		// If active 
		srcA *= (-1) ** ( srcInv[i] === true ? 1 : 0 );	// Polarity
		pyAttRequest(srcA, 'srcAmp', i);
		pyAttRequest(srcDelay[i]*1e-3, 'srcT0', i);		// Note: conversion from ms -> seconds
		pyAttRequest(srcFreq[i], 'srcFreq', i);
		pyAttRequest(srcType[i], 'srcType', i);
		// ... Sources get updated before each new run
	};
	// Update receivers
	for (var i = 0; i<NRec; i++){
		// Move or add a receiver
		if (i < fdtdObj.recN) { pyRecMove(recY[i], recX[i], i); 
		} else {	pyRecAdd(recY[i], recX[i]); }
		// Update settings
		var recA = recActive[i] === true ? 1 : 0;		// If active
		pyAttRequest(recA, 'recAmp', i);
		// ... Receivers get updated before each new run
	};
}

// Set mesh values (padding, admittance etc...)
function setMeshValues(doUpdateMesh=true) {
	printToDebug("Set mesh values");
	// Update Python values (with offline local values)
	fdtdObj.imageThreshold = imageThreshold*0.01;	// Convert from percentage to unity scalar
	fdtdObj.betaMode = betaMode;
	// If data stored in beta is actually NIAC
	if (doAbsCoeff) {
		fdtdObj.beta = abs2admit(beta);
		fdtdObj.betaBorder = abs2admit(betaBorder);
	} else {
		fdtdObj.beta = beta;
		fdtdObj.betaBorder = betaBorder;
	}
	// Update in Python - i.e. get new fdtdObj.mesh
	if (doUpdateMesh) {
		// (pass x and y mesh size - note: switch of x and y)
		fdtdObj.image2Mesh(null, null, Ny, Nx);
		// Request new image data (imReply() triggers prep of new mesh and re-plotting)
		pyImRequest();
	}
}

// Initial setup on receiving message from Python when loaded
function pyLoaded() {
	printToDebug("Initialising js script");
	// FDTD python object
	fdtdObj = pyscript.interpreter.globals.get('fdtd');
	// Define python functions
	//pyRunStep = pyscript.interpreter.globals.get('doRunStep');
	pyPRequest = pyscript.interpreter.globals.get('doPRequest');
	pyImRequest = pyscript.interpreter.globals.get('doImRequest');
	pyAttRequest = pyscript.interpreter.globals.get('doAttRequest');
	pyCreateOPFile = pyscript.interpreter.globals.get('doCreateOPFile');
	pySrcMove = pyscript.interpreter.globals.get('srcMove');
	pySrcAdd = pyscript.interpreter.globals.get('srcAdd');
	pyRecMove = pyscript.interpreter.globals.get('recMove');
	pyRecAdd = pyscript.interpreter.globals.get('recAdd');
	pyLoadImage = pyscript.interpreter.globals.get('loadImage');
	// Get all input parameters
	rtInputUpdate();
	olInputUpdate();
	// Set values, reset, and make fig
	updateButton();
	// Pre-load example if one is provided
	loadExample(loadEx);
	// Start listening for window resize (to trigger manual plot resizing due to aspect ratio not working)
	window.addEventListener("resize", onWindowResize);
	//// Enable buttons
	//document.querySelector("Run button").disabled = false;
	//document.querySelector("Reset button").disabled = false;
	//document.querySelector("Update button").disabled = false;
}

// Run simulation (until get stop message or reach end of sim)
async function runSim() {
	printToDebug("Run sim");
	// Start running
	isRunning = true;
	pyValidStep = fdtdObj.runStep();
	while (pyValidStep) {
		//var updatePlotThisLoop = fdtdObj.updatePlotThisLoop;
		var updatePlotThisLoop = (fdtdObj.loopNum+1)%plotIthUpdate == 0;
		if (updatePlotThisLoop) {
				mainHeader.innerHTML = mainHeaderPrefix + "Running";	// Update header
				tSimDivUpdate();										// Update time div
				pyPRequest();											// Get new p data
				updateFigData({'z': [pyZValues]}, fdtdFigLayer);		// Update the figure
				await sleep(plotSleepTime);
			};
		pyValidStep = fdtdObj.runStep();
		if (stopNextStep) {
			// Stop and reset loop counter
			fdtdObj.stop();
			fdtdObj.loopNum = 0;
			break;
		};
		if (fdtdObj.loopNum > maxSteps) {break;};
	}
	mainHeader.innerHTML = nextHeaderUpdate;
	// Check if any downloads
	doDownloads();
	isRunning = false;
}

// Trigger downloading of files
function doDownloads() {
	printToDebug("Trigger any downloads");
	// Note this is clunky
	if (mainHeader.innerHTML == mainHeaderPrefix + "Finished") {
		if (madeGif) { gifDownloadBut.click(); madeGif = false; }
		if (madeWav) { wavDownloadBut.click(); madeWav = false; }
	}
}

// Receive 'run' button press
function runButton() {
	printToDebug("Run button press");
	// If start of sim
	if (fdtdObj.loopNum==0) {
		// Run update to get all current values etc.
		updateButton();
		// Attempt to check and fix mesh
		checkMesh();
		// Get mesh ready
		fdtdObj.prepareMesh();
		// Check source(s) and receiver(s)
		var srcRecOnMesh = fdtdObj.srcRecOnMesh();
		if (srcRecOnMesh) { 
			passUserMessage("Source/receiver location warning. One or more source/receivers may be on a surface - try moving them in to 'free space'.")
			return;
		}
		// Update if making files to download
		downloadStatus();
	}
	// Reset this flag
	stopNextStep = false;
	// Set running to true if false (and vice-versa)
	fdtdObj.running = !fdtdObj.running;
	// Run sim if true
	if (fdtdObj.running) {
		mainHeader.innerHTML = mainHeaderPrefix + "Running";
		nextHeaderUpdate = mainHeaderPrefix + "Finished";
		//document.querySelector("Stop button").disabled = false;
		runSim();
	}
	else {
		nextHeaderUpdate = mainHeaderPrefix + "Paused";
	}
}

// Receive 'reset' button press
function resetButton() {
	printToDebug("Reset button press");
	// Reset everything, but don't set new values
	//nextHeaderUpdate = mainHeader.innerHTML;
	nextHeaderUpdate = mainHeaderPrefix + "Ready!!";
	resetAll();
}

// Receive 'stop' button press
async function stopButton(doReset=true) {
	printToDebug("Stop button press");
	// Stop sim
	stopNextStep = true;
	nextHeaderUpdate = mainHeaderPrefix + "Ready!!";
	// Reset everything
	if (doReset) { resetAll(); }
	//document.querySelector("Stop button").disabled = true;
}

// Receive 'update' button press
async function updateButton() {
	printToDebug("Update settings button press");
	// Stop everything
	stopButton(false);				// Don't reset as do this below
	// Set values
	setValues();
	// Now run reset
	nextHeaderUpdate = mainHeaderPrefix + "Ready!!";
	resetAll(false);				// Don't make new fig as do this below
	// Update mesh (padding, threshold, admittance etc...)
	setMeshValues();				// Triggers re-plotting
}

// Receive 'load file' button press
function loadFileButton() {
	printToDebug("Load file button press");
	// Stop everything
	// Get file name
	//file = loadFileBox.files[0];
	//if (file === undefined){ return }
	// Update header
	mainHeader.innerHTML = mainHeaderPrefix + "Loading...";
	nextHeaderUpdate = mainHeaderPrefix + "Ready!!";
	// NOTE: The rest is handled by Python
}

// UNUSED
// Receive 'update mesh' button press
function meshUpdateButton() {
	printToDebug("Prepare mesh button press");
	// Stop everything
	stopButton();
	// Prepare mesh for running sim
	fdtdObj.prepareMesh();
}

// Receive 'reset mesh' button press
function meshResetButton() {
	printToDebug("Reset mesh button press");
	// Stop everything
	stopButton();
	// Reset mesh
	nextHeaderUpdate = mainHeaderPrefix + "Ready!!";
	resetMesh();
}

// Display user info
function infoButton() {
	printToDebug("Info button press");
	alert(infoText);
}
		
// Render current image view (including shapes) to an image and update fig
function renderImageButton() {
	printToDebug("Render image button press");
	// Stop everything (no reset to avoid clearing fig)
	stopButton(false);
	// Get grid size
	if (renderPanZoom) {
		// ... including pan/zoom
		var vals = getRangeFromPlot();
		var xRangePlot = vals[0];
		var yRangePlot = vals[1];
		var NxPlot = vals[2];
		var NyPlot = vals[3];
		// Move source/receivers
		for (var i = 0; i<NSrc; i++) {
			var xi = Number(srcXBox[i].value);
			var yi = Number(srcYBox[i].value);
			srcXBox[i].value = xi-xRangePlot[0];
			srcYBox[i].value = yi-yRangePlot[0];
		}
		for (var i = 0; i<NRec; i++) {
			var xi = Number(recXBox[i].value);
			var yi = Number(recYBox[i].value);
			recXBox[i].value = xi-xRangePlot[0];
			recYBox[i].value = yi-yRangePlot[0];
		}
	} else {
		// ... without pan/zoom
		NxPlot = Nx;
		NyPlot = Ny;
		xRangePlot = [xValues[0], xValues[Nx-1]]
		yRangePlot = [yValues[0], yValues[Ny-1]]
	}
	// Adjust shape width according to plot size (roughly 1 pixel per 120 pixels grid size)
	var shapeWidth = Math.round(Math.sqrt(NxPlot*NyPlot)/125.0)
	shapeWidth = clamp(shapeWidth,2,6);
	var shapes = plotDiv.layout.shapes;
	//var XPlot = fdtdObj.X;	// Prev.
	var XPlot = X;				// Current
	if (shapes != undefined) {
		for (var i=0 ; i<shapes.length ; i++) {
			shapes[i]['line']['width'] = shapeWidth;
			shapes[i]['line']['color'] = "black";
			switch (shapes[i]['type']) {
				case "line":	// Fall through
				case "rect":	// Fall through
				case "circle":
					shapes[i]['x0'] = snapToGrid(shapes[i]['x0'], XPlot);
					shapes[i]['x1'] = snapToGrid(shapes[i]['x1'], XPlot);
					shapes[i]['y0'] = snapToGrid(shapes[i]['y0'], XPlot);
					shapes[i]['y1'] = snapToGrid(shapes[i]['y1'], XPlot);
					break;
				default :		// Otherwise do nothing
			}
		}
	}
	// Set cropped/stripped back layout
	var layoutUpdate = {
		shapes: shapes,
		width: NxPlot,
		height: NyPlot,
		margin: {l: 0, r: 0, b: 0, t: 0, pad: 0},
		plot_bgcolor: "white",
		xaxis: {
			range: xRangePlot,					// Range
			showgrid: false, 					// Grid
			zeroline: false, 					// Origin zero line
			visible: false,  					// Labels
			showline: false,					// Box bottom
			mirror: false,						// Box top
			ticks: "",							// No ticks
		},
		yaxis: {
			range: yRangePlot,					// Range
			showgrid: false, 					// Grid
			zeroline: false, 					// Origin zero line
			visible: false,  					// Labels
			showline: false,					// Box left
			mirror: false,						// Box right
			ticks: "",							// No ticks
		}
	};
	// Set colour scale so mesh surfaces are black
	meshColInvStatus = false;
	getGreyScale();
	// Update everything ready for saving
	updateFigLayout(layoutUpdate);
	updateFigData({visible: false, showscale: false}, fdtdFigLayer);
	updateFigData({visible: true, colorscale: [colorscaleGrey], zsmooth: false}, meshFigLayer);
	updateFigData({visible: false}, srcFigLayer);
	updateFigData({visible: false}, recFigLayer);
	// Save image and add to img div (Python listening for change)
	Plotly.toImage(plotDivId, {format:'png',height:NyPlot,width:NxPlot}).then(
		function(dataURL){imgDiv.src = dataURL;});
	// Note: above triggers new fig anyway, but this sets it back immediately
	// ... so the user doesn't see (for very long at least) the above edits
	rtMeshColInvStatus(false);
	makeFig();
}

