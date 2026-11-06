# PyScript examples - extras

Any extra potentially useful methods/techniques etc.

### My worker
( [Repository](my-worker/) | [Web page](https://sparky-10.github.io/code/pyscript-examples/extras/my-worker) )
Use of a [worker](https://docs.pyscript.net/2026.7.3/user-guide/workers/) to run Python code in a background thread. This prevents blocking of the main page thread, stopping the freezing of the page UI when longer blocks of code are run. Try running a longer 'calculation' in the worker thread and then immediately interacting with other elements of the page (e.g. chnaging the numbers and running a quicker calculation in the main thread), and vice-versa.

## License

[MIT](https://choosealicense.com/licenses/mit/)

