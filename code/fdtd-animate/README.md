# FDTD Animate web page

This page simulates a 2D sound world based on an input image, running 2D acoustic Finite Difference Time Domain (FDTD) code. There are loadable examples, or user images can be used. Mainly a bit of fun, but also for interest/understanding.

Note: 'use at your own risk'. No guarantee made of accurate predictions.

## FDTD

The simulation uses a 2D acoustic Finite Difference Time Domain (FDTD) model.

Details:
* Grid: basic rectangular
* Scheme: compact explicit standard leapfrog
* See e.g.: work of Konrad Kowalczyk
* Source(s): Gaussian derivative
* Boundary: no perfectly matched layer (PML)!!

## PyScript

This page uses PyScript [PyScript](https://pyscript.net/) to download and run Python code. Python is not required on the local machine, but note it can takes a short while to load and will downoad data on order of tens of MB.

Note: PyScript is developmental and constantly changing; I'll try to make sure it doesn't break!

## Python

The basic standalone FDTD code can be found in [pyFDTD](pyFDTD/).

## License

[MIT](https://choosealicense.com/licenses/mit/)
