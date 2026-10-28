# PyScript examples/templates

This repository contains example/template web pages using [PyScript](https://pyscript.net/) to allow Python code to be run in the browser. The primary aim is to enable simpler online sharing and demonstrating of science/engineering Python code, particularly for acoustics/audio applications, though examples may be useful for other purposes.

Each subfolder contains a different illustration of how PyScript could be used to perform a task to demonstrate a piece of code. The examples are intended to represent common tasks/applications (e.g. load->process->plot->download). The 'process' part of each example is intentionally simple and serves as a placeholder for editing and substituting in users own Python code. This allows the fast and simple creation of online demonstrations of users work.

Quick links:
* Hello, world! ( [Repository](hello-world/) | [Web page](https://sparky-10.github.io/code/pyscript-examples/hello-world) )
* Plot sum of harmonics ( [Repository](plot-sum-of-harmonics/) | [Web page](https://sparky-10.github.io/code/pyscript-examples/plot-sum-of-harmonics) )
* Code in my console ( [Repository](code-in-my-console/) | [Web page](https://sparky-10.github.io/code/pyscript-examples/code-in-my-console) )
* Analyse my wav 1 ( [Repository](analyse-my-wav-1/) | [Web page](https://sparky-10.github.io/code/pyscript-examples/analyse-my-wav-1) )
* Analyse my wav 2 ( [Repository](analyse-my-wav-2/) | [Web page](https://sparky-10.github.io/code/pyscript-examples/analyse-my-wav-2) )
* Filter my wav ( [Repository](filter-my-wav/) | [Web page](https://sparky-10.github.io/code/pyscript-examples/filter-my-wav) )
* Plot array response ( [Repository](plot-array-response/) | [Web page](https://sparky-10.github.io/code/pyscript-examples/plot-array-response) )
* Animate my model ( [Repository](animate-my-model/) | [Web page](https://sparky-10.github.io/code/pyscript-examples/animate-my-model) )

See examples in subfolders for further info.

Note:
* All examples are basic illustrations of use of PyScript, and not necessarily fully error checked (so bugs may exist)
* Code may not always be Pythonic and/or preferred PyScript way of doing things
* This is not a tutorial in HTML/CSS/web page design (pages are intentionally basic/plain - see other resources for making pages more attractive/functional)

## What is PyScript

PyScript is:
* An open-source framework/platform for running Python directly in a web browser
* Python scripts running directly in the browser - not on a server or local Python installation
* Use of Pyodide (CPython compiled to WebAssembly) or MicroPython to execute code
* Python able to inspect, manipulate, and interact with web page elements and events

Essentially, a few files hosted statically online can produce a Python enabled web page.

Resources:
* [pyscript.net](https://pyscript.net/) - The home of PyScript, including manuals
* [pyscript.com](https://pyscript.com/) - Hosting service to write, run, and share code

## Getting started

The absolute basics of a web page for running PyScript are given in [Hello, world!](hello-world/).

See also: [pyscript.net docs](https://docs.pyscript.net/2026.7.3/)

### The index file

All web pages need an index.html file. The only requirements to add basic PyScript functionality to a page are:
* A few lines in the header
* A configuration element or file (if using anything beyond plain Python - e.g. importing a package)
* A script element containing or referencing some Python code

An example file structure looks something like this:

```
<!doctype html>
<html lang="en">
<head>
    <!--Basic recommended meta and title tags-->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>My PyScript Page</title>
    <!-- Fetch and use PyScript CSS and JS files (in this case version 2026.7.3) -->
    <link rel="stylesheet" href="https://pyscript.net/releases/2026.7.3/core.css">
    <script type="module" src="https://pyscript.net/releases/2026.7.3/core.js"></script>
</head>
<!--Inline configuration (TOML format)-->
<py-config>
packages = ["numpy"]
</py-config>
<body>
    <h1>This is a PyScript enabled page</h1>
    <!-- Inline Python code-->
    <script type="py">
        # Your code here
    </script>
</body>
</html>
```

#### Header

The lines in the example above fetch and initialise the required files/code to run PyScript.

Note: PyScript is constantly evolving. Web pages should specify a fixed version of PyScript (2026.7.3 in the example above, previous use of 'latest' is now deprecated) to avoid new release syntax/functionality changes breaking any existing code.

Note: All examples here are written using PyScript 2026.7.3 (see release versions [here](https://github.com/pyscript/pyscript/releases)).

#### Configuration

A PyScript page needs to configure it's Python environment (unless the absolute basic/default PyScript functionality is required - i.e. no imported packages, external files etc..).

The example above shows an inline configuring of PyScript to include the package "NumPy". The preferred/recommended method for configuration is to specify as a separate file, which is then referenced by a PyScript script tag (see below). Other aspects can be configured including Python interpreter, accessible files, plugins etc. (see later examples and online [docs](https://docs.pyscript.net/2026.7.3/user-guide/configuration/)). In the case of 'workers' (see later examples), multiple PyScript instances on the same page can even be configured differently.

Note: PyScript may be limited in terms of use of non-standard Python packages. For a list of supported packages see [here](https://packages.pyscript.net/).

#### Python code

Python code is included through use of a script tag. The example above specifies a script type "py" (which differentiates it from a default JS script tag). Python code can then be included within the script tag as inline code (see [Hello, world!](hello-world/)). As above, however, the preferred/recommended method for including Python code is to specify a separate file, for example:

```
<script type="py" src="./main.py" config="./myConfig.toml">
</script>
```

Note: the default WebAssembly Python distribution used is Pyodide. The other main distribution available through PyScript is MicroPython, which is accessible by specifying type="mpy" in a script tag. This is largely not used here (there is one example in [Code in my console](code-in-my-console/)), but may be of interest if a more limited lighter weight version of Python is desirable - e.g. for quicker load time etc.

### Running the page

#### Basic code

For debugging purposes, if the code does not need additional files then simply opening the index.html file in a browser should work. [Hello, world!](hello-world/) is an example of this.

#### Running on a web server

For all but the most basic pages, and to share the page online, it is necessary to host the page on a web server. Some resources for doing this include:
* [pyscript.com](https://pyscript.com/) (specifically created for PyScript hosting/developing/sharing)
* [CodePen](https://codepen.io/trending)
* Any static web host (e.g. [GitHub Pages](https://docs.github.com/en/pages) like this page)

Alternatively, for writing/debugging, pages can be served locally using Python. If you have Python installed open a terminal pointed to the same directory as your files, and run the following:

```
python3 -m http.server
```

The page should then be accessible through a browser at [http://localhost:8000](http://localhost:8000).

You will need to refresh the browser after any changes are made. A hard refresh is sometimes needed when cached data persists.

#### Web developer tools

The web developer tools are browser specific, but often accessed via the F12 key (Windows/Linux).

Most browsers will have a "disable cache" option, which is a more reliable option than hard refreshing. When persistent cache issues arise, using a browsers private mode may also help.

A useful tool for debugging is the console which can be used to see errors, warnings and debug messages (note: this is where Python's standard 'print' messages appear; see later examples). There are also usually other useful tools for inspecting elements and their attributes/properties etc. 

## Notes

### Loading

Load time can be a minor issue with some 'heavier' pages, at least from a user experience point of view. The number and size of packages to download/initialise is often a cause of this, which is evident when using packages such as SciPy. If the use of a heavy package is minimal, replacing with an alternative package or user written code that achieves the same/similar may be useful (though sticking with the simpler more familiar package for writing the initial page is still advised).

It is also useful to let the user know when the page is loading, both so they don't think the page is broken and so buttons etc. aren't pressed ahead of Python code being ready. Later examples here use a splash screen to achieve this (firstly a simpler version that listens for when PyScript is initialised/ready, and later a version closed when the Python code has actually finished running).

### Prettifying & functional compatibility

The web page design here is intentionally simple and minimal in nature. Pages can clearly be made more attractive through HTML/CSS editing, as well as made more widely cross-platform/browser/device/display compatible (e.g. resizing/reorganising according to screen/device info). There are plenty of online resources that can help with this, and which could be used to create pages to which PyScript code is then added.

### Testing

This code has been primarily tested using Firefox and/or Chrome, run on Ubuntu 24.04 on a laptop/desktop.

## License

[MIT](https://choosealicense.com/licenses/mit/)

