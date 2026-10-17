# Analyse my wav 2

This is an example/template web page using [PyScript](https://pyscript.net/) to allow Python code to be run in the browser.

See:
* [Web page](https://sparky-10.github.io/code/pyscript-examples/analyse-my-wav-2) - Open working web page
* [Main repository](../) - For further examples/details

## This example

This example allows the user to:
* Load a ".wav" audio file from the user's system
* Do basic 'analysis' on the audio signal
* View output on screen of some basic signal statistics
* View a plot of the audio signal and analysis results

## Use case(s)

Basic upload, process/analyse based on user settings, and plot (effectively combined version of [Plot sum of harmonics](../plot-sum-of-harmonics) and [Analyse my wav 1](../analyse-my-wav-1)). Could be used to e.g. highlight areas of a plot where:
* Audio metric(s) (e.g. speech intelligibility) exceed a certain threshold
* Sound events are detected (e.g. speech, wind noise etc.)
* etc...

## Methods used

* Use of alternate package for ".wav" load (uses soundfile because SciPy can be 'heavy' and can sometimes cause page to load slowly)
* Moving of functions to external utility file ("ps_tools.py")<sup>#</sup>
* Function to constrain input received from page elements - e.g. ensure entered value is within defined range 
* Status updates to screen to let user know what's happening

<sup>#</sup>Note: file located in separate [util](../util) folder shared by all examples (see config). 

## Notable improvements in later examples

* Improved splash screen (that closes when Python code has finished running, not just when PyScript is initialised)
* Presets loadable from URL
* Improved plotting for faster/smoother updates
* File download
* Extended debugging

## Packages

* NumPy
* soundfile
* Matplotlib

## License

[MIT](https://choosealicense.com/licenses/mit/)

