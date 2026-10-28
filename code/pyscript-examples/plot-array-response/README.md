# Plot array response

This is an example/template web page using [PyScript](https://pyscript.net/) to allow Python code to be run in the browser.

See:
* [Web page](https://sparky-10.github.io/code/pyscript-examples/plot-array-response) - Open working web page
* [Main repository](../) - For further examples/details

## This example

This example allows the user to:
* Set inputs (number of sources, source spacing, individual source amplitudes, and frequency)
* View a plot of the array response
* Choose plot display method (to demonstrate the difference: "Matplotlib replace" vs "Matplotlib update" vs [https://plotly.com/python/](Plotly))

Note: the difference between Matplotlib methods is negligible as the re-rendering of plot image to page is the limiting factor.

## Use case(s)

Plotting of analytical/numerical model predictions based on user settings (similar to [Plot sum of harmonics](../plot-sum-of-harmonics)), e.g.:
* Impedance, absorption coefficient etc. of surfaces
* Directivity plots of loudspeaker models, diffuser scattering, transducer arrays etc.
* Insertion/transmission loss of silencers, partitions, structures etc.
* etc...

## Methods used

* Faster/smoother plot updates using [https://plotly.com/python/](Plotly) (interactive plot rather than re-rendering)<sup>#</sup>
* Matplotlib update plot method (note: little real benefit, but can be neater)
* Extended adding/manipulating of HTML elements on page
* Extended loading of Presets from URL
* Extended debug print outs (to further levels of verbosity/detail, including info from within called functions)

<sup>#</sup>Note: uses Plotly Python package (defined in config file) as well as Plotly.js (defined in index header) - see code. Other alternatives to the use of Plotly include [https://bokeh.org/](Bokeh), [https://panel.holoviz.org/](Panel), [https://hvplot.holoviz.org/en/docs/latest/](hvPlot) etc. (see e.g. [pyscript.com](https://pyscript.com/) examples).

## Notable improvements in later examples

* Fetching of file(s) from external resources
* Asynchronous plot updates

## Packages

* NumPy
* Matplotlib
* Plotly

## License

[MIT](https://choosealicense.com/licenses/mit/)

