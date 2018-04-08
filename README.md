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
qsub -I -A $PROJECT -l nodes=1,walltime=01:00:00 -lfeature=gpudefault -lgres=atlas1 -q debug
```
Create your YANK project software working directory and install miniconda
```bash
export PROJDIR="$PROJWORK/$PROJECT/"
cd $PROJDIR/yank
mkdir `whoami`
cd `whoami`
wget http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda3.sh
bash miniconda3.sh -b -p miniconda3
```
Set the miniconda paths, switch to gnu module environment, and enable CUDA module
```bash
# Set paths
export PROJECT="chm126"
export USERNAME="`whoami`"
export SOFTWARE="$PROJWORK/$PROJECT/yank/$USERNAME"
export MINICONDA3="$SOFTWARE/miniconda3"
export PATH="$MINICONDA3/bin:$PATH"
# Titan nodes have messed-up paths that differ from login node, so we also need to set LD_LIBRARY_PATH
export LD_LIBRARY_PATH="$MINICONDA3/lib:$LD_LIBRARY_PATH"
export SCRATCH="/lustre/atlas/scratch/$USERNAME/$PROJECT/"

# Switch to gnu module environment
module remove PrgEnv-pgi
module add PrgEnv-gnu
module add cray-mpich

# Configure CUDA
module load cudatoolkit
export OPENMM_CUDA_COMPILER=`which nvcc`
```
Install YANK and its dependencies
```bash
# Set LD_LIBRARY_PATH because paths are otherwise messed up
# Add path
# WARNING: This path may need to be edited based on the PREFIX printed above
conda config --add channels omnia --add channels conda-forge
conda config --add channels omnia/label/dev
conda update --yes --all
# Install yank
conda install --yes yank
# Remove openmm and install a CUDA 7.5 version
conda remove --yes --force openmm 
conda install --yes --no-deps openmm-cuda75
# Test YANK to make sure CUDA platform is available
# Note that nvidia-smi will not be available---that is normal and will trigger a warning that is expected
aprun -n 1 yank selftest
```
Configure and build custom mpi4py
```bash
# Remove mpi4py and install special version for titan
# Make sure to remove glib, since it breaks `aprun`
conda remove --yes --force glib mpi mpich mpi4py

# Build and install special mpi4py for titan
cd $SOFTWARE
wget https://bitbucket.org/mpi4py/mpi4py/downloads/mpi4py-3.0.0.tar.gz -O mpi4py-3.0.0.tar.gz
tar zxf mpi4py-3.0.0.tar.gz
cd mpi4py-3.0.0

cat >> mpi.cfg <<EOF
[cray]
mpi_dir              = /opt/cray/mpt/7.6.3/gni/mpich-gnu/4.9/
mpicc                = cc
mpicxx               = CC
extra_link_args      = -shared
include_dirs         = %(mpi_dir)s/include
libraries            = mpich
library_dirs         = %(mpi_dir)s/lib/shared:%(mpi_dir)s/lib
runtime_library_dirs = %(mpi_dir)s/lib/shared
EOF

python setup.py build --mpi=cray
python setup.py install
```
Grab the mutants data
```
git clone https://github.com/choderalab/kinase-resistance-mutants
cd kinase-resistance-mutants/hauser-abl-benchmark/input_files
```
Here's a TITAN run batch script for 8 nodes for 1 hour:
```bash
#!/bin/bash
#    Begin PBS directives
#
# Account to charge: our project number
#PBS -A chm126
#
# Set job name
#PBS -N yank
#
# Capture output and error
#PBS -j oe
#
# Set walltime and number of nodes
# Runtime limit is based on number of nodes requested:
# https://www.olcf.ornl.gov/for-users/system-user-guides/titan/running-jobs/#titan-scheduling-policy
# Jobs can be chained so that the next job starts when the first one terminates.
#PBS -l walltime=01:00:00,nodes=8
#
# Use atlas scratch storage
#PBS -l gres=atlas1%atlas2
#
# Start GPUs in shared mode for YANK to work
#PBS -l feature=gpudefault
#
#    End PBS directives and begin shell commands

# Set paths
export PROJECT="chm126"
export USERNAME="`whoami`"
export SOFTWARE="$PROJWORK/$PROJECT/yank/$USERNAME"
export MINICONDA3="$SOFTWARE/miniconda3"
export PATH="$MINICONDA3/bin:$PATH"
# Titan nodes have messed-up paths that differ from login node, so we also need to set LD_LIBRARY_PATH
export LD_LIBRARY_PATH="$MINICONDA3/lib:$LD_LIBRARY_PATH"
export SCRATCH="/lustre/atlas/scratch/$USERNAME/$PROJECT/"

# Configure CUDA
module load cudatoolkit
export OPENMM_CUDA_COMPILER=`which nvcc`
echo $OPENMM_CUDA_COMPILER

# Set up mpi environment
module remove PrgEnv-pgi
module add PrgEnv-gnu
module add cray-mpich

# Set the OpenEye license, but not all the openeye tools work here
export OE_LICENSE="$SOFTWARE/openeye/oe_license.txt"

# Change directory to working directory
cd $SCRATCH/yank-examples/examples/hydration/freesolv

# Run YANK, one MPI process per node
aprun -n $PBS_NUM_NODES -N 1 -d 16 yank script --yaml=sams.yaml
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
