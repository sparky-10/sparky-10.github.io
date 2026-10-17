# Filter my wav

This is an example/template web page using [PyScript](https://pyscript.net/) to allow Python code to be run in the browser.

See:
* [Web page](https://sparky-10.github.io/code/pyscript-examples/filter-my-wav) - Open working web page
* [Main repository](../) - For further examples/details

## This example

This example allows the user to:
* Load page using text appended to URL to set initial page settings 
* Load a ".wav" audio file from the user's system
* See plots of the time and frequency domain response(s)
* Set the properties of a basic Butterworth filter (type, order, cut-off frequencies)
* Filter the input signal and plot the result
* Download the filtered signal as a ".wav" file (Note: file output is float type not PCM regardless of upload file type, but simple to alter if required)

## Use case(s)

Basic upload, process, plot, and download. Processing (filtering) could be replaced with code such as:
* Auralisation
* Speech extraction
* Noise reduction
* etc...

## Methods used

* Improved 'loading' splash screen - screen is closed at end of PyScript block to ensure code has been executed
* Presets loadable from URL (try appending e.g. "?filterType=3&filterOrder=5", or "?N_TRIM=50000000")
* File download (".wav" in example, but extendable to other file types)
* Debug extended to use verbosity (e.g. view web developer console and append "?DEBUG=1" for basic and "?DEBUG=2" for verbose debug info, otherwise here debug is disabled)

## Notable improvements in later examples

* Improved plotting - Matplotlib plots updated rather than replaced on each input change, or use of more interactive methods (see Plotly example(s))
* Extended adding/manipulating of HTML elements
* Extended loading of Presets from URL
* Extended debug (levels of verbosity/detail)

## Non-standard library packages

* NumPy
* SciPy
* Matplotlib

## License

[MIT](https://choosealicense.com/licenses/mit/)

