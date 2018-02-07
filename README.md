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

## Installing YANK on Titan 

```bash
# Start an interactive test run
qsub -I -A $PROJECT -l nodes=1,walltime=00:30:00 -q debug

# Set the project accounting name
export PROJECT="chm126"

# MANUAL STEP: Get the working directory jobs are launched from by recording this directory
# Note that the directory `aprun` lauches into may be DIFFERENT from $MEMBERWORK
# If that happens, and we install miniconda in original $MEMBERWORK, libraries will not be found when running yank
aprun -n1 pwd
export MEMBERWORK=<directory from above>

# Install Python 3.x miniconda in shared path $MEMBERWORK/$PROJECT
cd $MEMBERWORK/$PROJECT
wget http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda3.sh
export MINICONDA3="$MEMBERWORK/$PROJECT/miniconda3"
bash miniconda3.sh -b -p $MINICONDA3
export PATH="$MINICONDA3/bin:$PATH"
conda config --add channels omnia --add channels conda-forge
conda update --yes --all
# Install latest OpenMM from dev channel
conda install -c omnia/label/dev --yes openmm
# Install yank
conda install --yes yank
# Install CUDA toolkit (optional if using OpenCL)
module load cudatoolkit
# Launch Python on one process
aprun -n1 python -m simtk.testInstallation
```
