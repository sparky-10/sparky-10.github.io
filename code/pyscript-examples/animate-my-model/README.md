# Animate my model

This is an example/template web page using [PyScript](https://pyscript.net/) to allow Python code to be run in the browser.

See:
* [Web page](https://sparky-10.github.io/code/pyscript-examples/animate-my-model) - Open working web page
* [Main repository](../) - For further examples/details

This is effectively a much simpler version of an older page "FDTD Animate" ( [page](https://sparky-10.github.io/code/fdtd-animate/) | [repository](https://github.com/sparky-10/pyFDTD)), though note this uses a much earlier version of PyScript and is written using both JS and PyScript.

## This example

This example allows the user to:
* Set numerous page inputs
* Run an animated plot of a 1D FDTD model
* Download a ".wav" receiver response file

## Use case(s)

Animating of analytical/numerical model prediction (similar to [Plot array response](../plot-array-response)), e.g.:
* Time domain response of simulation
* Time history of converging prediction
* etc...

## Methods used

* Fetches file from GitHub repository (pinned to specific version)
* Asyncio for asynchronous plotting

## Notable improvements in later examples

This will be updated as new examples are added.

## Packages

* NumPy
* SciPy
* Matplotlib
* Pillow
* Plotly

## License

[MIT](https://choosealicense.com/licenses/mit/)
