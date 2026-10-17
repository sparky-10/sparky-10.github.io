# Plot sum of harmonics

This is an example/template web page using [PyScript](https://pyscript.net/) to allow Python code to be run in the browser.

See:
* [Web page](https://sparky-10.github.io/code/pyscript-examples/plot-sum-of-harmonics) - Open working web page
* [Main repository](../) - For further examples/details

## This example

This example allows the user to:
* Set inputs (wave type: sawtooth/triangular/square, and number of harmonics)
* View a plot of the sum of the first N harmonics of the harmonic series

## Use case(s)

Plotting of analytical/numerical model predictions based on user settings, e.g.:
* Impedance, absorption coefficient etc. of surfaces
* Directivity plots of loudspeaker models, diffuser scattering, transducer arrays etc.
* Insertion/transmission loss of silencers, partitions, structures etc.
* etc...

## Methods used

* Inline code (can be opened locally direct in the browser)
* Event decorators (including stacking) to trigger code execution on page activity (i.e. user input changes)
* Matplotlib for plotting
* Printing of messages to the web developer tools console (e.g. for debugging)

## Notable improvements in later examples

* Splash screen - to let user know when page is loading and stop any page interaction until page is ready
* Inline code moved to separate files (inline code can be useful for early development/debugging, but recommended method is to move to separate Python/config files)
* Console interactivity
* Checking/constraining of user input values (e.g. try typing in invalid entry to number of harmonics input)
* Improved plotting - Matplotlib plots updated rather than replaced on each input change, or use of more interactive methods (see Plotly)

## Packages

* NumPy
* Matplotlib

## License

[MIT](https://choosealicense.com/licenses/mit/)
