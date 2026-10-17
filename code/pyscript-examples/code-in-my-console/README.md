# Code in my console

This is an example/template web page using [PyScript](https://pyscript.net/) to allow Python code to be run in the browser.

See:
* [Web page](https://sparky-10.github.io/code/pyscript-examples/code-in-my-console) - Open working web page
* [Main repository](../) - For further examples/details

## This example

This example allows the user to:
* Use an interactive console/terminal environment (familiar to many Python users)
* Try pre-loaded code

## Use case(s)

A simple way of allowing a user to explore code without having to create a more functional web page.

## Methods used

Referenced via script tag in HTML:
* Python code and configuration moved to separate files
* Use of terminal script type
* Use of workers (which is expanded upon in later examples, see [docs](https://docs.pyscript.net/2026.7.3/user-guide/workers/))<sup>#</sup>
* Use of [MicroPython](https://micropython.org/) (type="mpy") which provides faster startup with a smaller footprint when only core Python functionality is required

Plus:
* Inclusion of additional required files in configuration file

<sup>#</sup>Note:
* The use of the worker flag is necessary to allow the terminal to run outside of the main page thread and stop the terminal blocking page functionality
* Workers may not work correctly unless hosted on proper server (e.g. this was written using pyscript.com rather than using Python "http.server" local server method)

## Notable improvements in later examples

* Splash screen - to let user know when page is loading and stop any page interaction until page is ready
* Console: page interaction (plotting, user inputs etc), access to files (e.g. via user upload)
* Extended use of workers (to allow more responsive pages that don't get blocked by more heavy running Python code)
* Data passing between workers

## Packages

This example uses Micropython, which uses core Python only.

## License

[MIT](https://choosealicense.com/licenses/mit/)
