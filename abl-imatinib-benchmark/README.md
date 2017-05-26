# OpenMM benchmarking scripts for INCITE-2017 proposal

This benchmark is for an Abl:imatinib simulation in explicit solvent containing 46648 atoms.

## Manifest

* `benchmark.py` - run this script to benchmark performance on the default GPU platform
* `prepare-serialized-files.py` - prepare XML serialized files

## Usage

To benchmark local hardware, first install OpenMM. 
For systems with CUDA 8.0, the easiest way to do this is to first install [miniconda](https://conda.io/miniconda.html) Python and then use the provided [`conda` package manager](https://conda.io/docs/using/pkgs.html) to install [openmm](https://anaconda.org/omnia/openmm) from the `omnia` channel:
```bash
conda install -c conda-forge -c omnia openmm
```
For systems with other CUDA versions, you must currently [compile OpenMM from source](http://docs.openmm.org/7.1.0/userguide/library.html#compiling-openmm-from-source-code); note the prerequisites for building.

You can then run the benchmark script:
```bash
python benchmark.py
```
which should produce output like this:
```
-bash-4.1$ python benchmark.py
Deserializing simulation...
System contains 46648 atoms.
Using platform "CUDA".
Warming up integrator to trigger kernel compilation...
Benchmarking...
completed     5000 steps in   26.521 s : performance is   32.578 ns/day
```

## Rebuilding the XML files

You will require `openmmtools` to do this.
Simply run
```
python prepare-serialized-files.py
```


