# Analyse my wav 1

This is an example/template web page using [PyScript](https://pyscript.net/) to allow Python code to be run in the browser.

See:
* [Web page](https://sparky-10.github.io/code/pyscript-examples/analyse-my-wav-1) - Open working web page
* [Main repository](../) - For further examples/details

## This example

This example allows the user to:
* Upload file from user's system (".wav" audio file in example, but extendable to other file types)
* Do (very!) basic 'analysis' on the audio signal (note: input gets summed to mono in this example)
* View output on screen of some signal statistics

## Use case(s)

Basic upload, and process/analyse. Processing could be replaced with code such as:
* Audio metrics of any type (e.g. speech intelligibility)
* Sound event detection (e.g. presence of speech, wind noise etc.)
* etc...

## Methods used

* Simple splash screen - to let user know when page is loading and stop any page interaction until page is ready (note improvements in later versions)
* Upload of audio file (".wav") from user's local system

## Notable improvements in later examples

* Improved splash screen (that closes when Python code has finished running, not just when PyScript is initialised)
* Use of alternate library package to load ".wav" file (SciPy can be 'heavy' and cause page to load slowly)
* On screen user updates
* Extended debugging

## Packages

* NumPy
* Scipy

## License

[MIT](https://choosealicense.com/licenses/mit/)
