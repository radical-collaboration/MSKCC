# MSKCC

This repository is curated by members of the RADICAL team at Rutgers University and The Chodera Lab at Memorial Sloan Kettering Cancer Center 

## Manifest

* `abl-imatinib-benchmark` - OpenMM benchmarking scripts and input files

## Running OpenMM--7.2 benchmarks against CUDA/7.5 on Titan 

```bash
# Set the project accounting name
export PROJECT="chm126"

# Install Python 2.7 miniconda in shared path /ccs/proj/mskcc/chm126/miniconda
wget http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh -O miniconda.sh
bash miniconda.sh -b -p /ccs/proj/mskcc/$PROJECT/miniconda
# Create 'venv' environment and add omnia/conda-forge channels
conda create --name venv
conda config --add channels omnia --add channels conda-forge
# Install OpenMM for CUDA 7.5
conda install -c omnia/label/dev --yes openmm-cuda75
# Submit an interactive test run
qsub -I -A $PROJECT -l nodes=1,walltime=00:30:00 -q debug
# PBS batch script contents
module load python_anaconda
module load cudatoolkit
source activate venv
export PATH=/ccs/proj/$PROJECT/mskcc/miniconda/bin:$PATH
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/ccs/proj/<project_id>/mskcc/miniconda/lib
export PYTHONPATH=$PYTHONPATH:/ccs/proj/<project_id>/mskcc/miniconda/lib/python2.7/site-packages/
PYTHONPATH=$PYTHONPATH:/sw/xk6/python_anaconda/2.3.0/sles11.3_gnu4.8.2/lib/python2.7/site-packages/
export OPENMM_CUDA_COMPILER=/opt/nvidia/cudatoolkit7.5/7.5.18-1.0502.10743.2.1/bin/nvcc
# Launch Python on one process
aprun -n1 python -m simtk.testInstallation
```

## Installing YANK on Titan within lustre project directory

This installs the latest YANK with the OpenMM 7.2 dev package (which requires CUDA 9.0, so only OpenCL is available)

Note that `$HOME` may not be available on the compute nodes. We will have to figure it out from running
```bash
# Set the project accounting name
export PROJECT="chm126"

# Start an interactive test run
qsub -I -A $PROJECT -l nodes=1,walltime=00:30:00 -lfeature=gpudefault -lgres=atlas1 -q debug
# Figure out where jobs actually launch
aprun -n1 pwd
```
Use the output of `pwd` to set `$HOME`:
```bash
# MANUAL STEP: Change the path to the output of your `pwd`
export HOME=/lustre/atlas/scratch/jchodera1/chm126
cd $HOME
# Other environment variables we will need
export MINICONDA3="$HOME/miniconda3"
export PATH="$MINICONDA3/bin:$PATH"
# Titan nodes have messed-up paths that differ from login node, so we also need to set LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$MINICONDA3/lib:$LD_LIBRARY_PATH

```
Install YANK and its dependencies
```bash
# Go to new home
# Install Python 3.x miniconda 
# TODO: Should we do this in shared path $MEMBERWORK/$PROJECT instead of new HOME?
wget http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda3.sh
aprun -n1 bash miniconda3.sh -b -p miniconda3
# Set LD_LIBRARY_PATH because paths are otherwise messed up
# Add path
# WARNING: This path may need to be edited based on the PREFIX printed above
conda config --add channels omnia --add channels conda-forge
conda config --add channels omnia/label/dev
conda update --yes --all
# Install latest OpenMM from dev channel
conda install --yes openmm
# Install yank
conda install --yes yank
# Remove glib (and things that depend on it), since it breaks `aprun`
conda remove --yes glib
# Force reinstall YANK without reinstalling glib
conda install --no-deps --yes yank
# MANUAL STEP: Edit parmed installation to reflect this change: https://github.com/ParmEd/ParmEd/pull/957
# $MINICONDA/lib/python3.6/site-packages/parmed/gromacs/gromacstop.py
# Test YANK
aprun -n 1 yank selftest
```
Grab the mutants
```
git clone https://github.com/choderalab/kinase-resistance-mutants
cd kinase-resistance-mutants/hauser-abl-benchmark/input_files
```
Here's a TITAN run batch script for 16 nodes for 1 hour:
```bash
#!/bin/bash
#    Begin PBS directives
#PBS -A chm126
#PBS -N yank-imatinib
#PBS -j oe
#PBS -l walltime=1:00:00,nodes=16
#PBS -l gres=atlas1%atlas2
#PBS -l feature=gpudefault
#    End PBS directives and begin shell commands
# MANUAL STEP: Change the path to the output of your `pwd`
export HOME=/lustre/atlas/scratch/jchodera1/chm126
export MINICONDA3="$HOME/miniconda3"
export PATH="$MINICONDA3/bin:$PATH"
export LD_LIBRARY_PATH=$MINICONDA3/lib:$LD_LIBRARY_PATH
date
cd $HOME/kinase-resistance-mutants/hauser-abl-benchmark/input_files
# Specify only one job per node with -j 1
aprun -n $PBS_NUM_NODES -j 1 yank script --yaml=imatinib.yaml
```
Here's the modified YANK input file:
```YAML
# I've had trouble avoiding a warning that OEQuacPac isn't installed on TITAN even when installed,
# So let's pre-charge the ligands and just pass through charges if we can.
#    openeye:
#      quacpac: am1-bcc
    antechamber:
      charge_method: null

```
