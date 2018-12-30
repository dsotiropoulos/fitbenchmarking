[![Build Status](https://travis-ci.com/mantidproject/fitbenchmarking.svg?branch=master)](https://travis-ci.com/mantidproject/fitbenchmarking) [![Coverage Status](https://coveralls.io/repos/github/mantidproject/fitbenchmarking/badge.svg?branch=master)](https://coveralls.io/github/mantidproject/fitbenchmarking?branch=master)

# FitBenchmarking
FitBenchmarking is a tool for comparing different minimizers/fitting software based on their accuracy and runtimes.


## Quick Start
[![Python 2.7](https://img.shields.io/badge/python-2.7-blue.svg)](https://www.python.org/downloads/release/python-2715/) will be needed for running/installing this. Instructions for setting up python are available [here](https://github.com/mantidproject/fitbenchmarking/wiki/Setting-up-Python).

1. Download this repository or clone it using [git](https://git-scm.com/):
`git clone https://github.com/mantidproject/fitbenchmarking.git`
2. Open up a terminal (command prompt) and go into the `fitbenchmarking` directory.
3. Once you are in the right directory, type `python setup.py install`.
4. Install mantid, platform specific instructions [here](https://github.com/mantidproject/fitbenchmarking/wiki/Installing-Mantid).
5. Open the mantidpython terminal
    * Ubuntu: in a normal terminal cd to /opt/Mantid/bin and run `./mantidpython`
    * Windows: go to where you installed Mantid and search for a file called `mantidpython`

Finally, in this terminal, run `example_scripts/example_runScript.py`, located in the fitbenchmarking folder. This example script fit benchmarks Mantid using all the available minimizers. The resulting tables can be found in `example_scripts/results`.

## FitBenchmarking Scipy
The `example_runScript` file can be changed such that it benchmarks scipy instead of mantid (details provided in the file itself). To avoid a known issue with the mantidpython console on Windows please do the following:

1. Start the mantidpython console as admin.
2. Run the follwoing commands:
    - `!python -m pip install --upgrade pip`
    - `!python -m pip install scipy --upgrade`
    - `!python -m pip install numpy upgrade`
3. Restart the mantidpython terminal.

This is required on Windows since mantidpython on this platform comes with an older version of scipy. **Linux works without doing the steps described above, given that you followed the setup instructions in the eariler section.**

## Tool Description
The tool creates a table/tables that shows a comparison between the different minimizers available in a fitting software (e.g. scipy or mantid), based on their accuracy and/or runtimes.
An example of a table is:

![Example Table](docs/example_table.png)

This is the result of fitbenchmarking mantid on a set of neutron data. The results are normalised with respect to the best minimizer per problem. The problem names link to html pages that display plots of the data and the fit that was performed, together with initial and final values of the parameters. Here is an example of the final plot fit.

![Example Plot](docs/example_plot.png)

## Currently Benchmarking
<div style="text-align: center">
<a href="http://www.mantidproject.org/Main_Page">
<img width="100" height="100" src="https://avatars0.githubusercontent.com/u/671496?s=400&v=4"></a>
<a href="https://www.scipy.org/">
<img width="100" height="100" src="http://gracca.github.io/images/python-scipy.png">
</a>
</div>
