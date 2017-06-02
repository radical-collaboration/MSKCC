# MSKCC

This repository is curated by members of the RADICAL team at Rutgers University and The Chodera Lab at Memorial Sloan KetteringCancer Center 

## Manifest

* `abl-imatinib-benchmark` - OpenMM benchmarking scripts and input files

## Running OpenMM--7.2 benchmarks against CUDA/7.5 on Titan 

* `wget http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh -O miniconda.sh`
* `bash miniconda.sh -b -p /ccs/proj/<project_id>/miniconda2`
* `conda create --name venv`
* `conda config --add channels omnia --add channels conda-forge`
* `conda install -c omnia/label/dev --yes openmm-cuda75`

* `qsub -I -A <project_id> -l nodes=1,walltime=00:30:00 -q debug`

`module load python_anaconda`
`module load cudatoolkit`
`source activate venv`

export PATH=/ccs/proj/<project_id>/mskcc/miniconda/bin:$PATH
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/ccs/proj/<project_id>/mskcc/miniconda/lib
export PYTHONPATH=$PYTHONPATH:/ccs/proj/<project_id>/mskcc/miniconda/lib/python2.7/site-packages/
PYTHONPATH=$PYTHONPATH:/sw/xk6/python_anaconda/2.3.0/sles11.3_gnu4.8.2/lib/python2.7/site-packages/
export OPENMM_CUDA_COMPILER=/opt/nvidia/cudatoolkit7.5/7.5.18-1.0502.10743.2.1/bin/nvcc

aprun -n1 python -m simtk.testInstallation
