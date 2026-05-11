#!/bin/bash

# ===== OpenMPI Setup =====
export OMPI_HOME=/workspace/openmpi-5.0.9
export PATH=$OMPI_HOME/bin:$PATH
export LD_LIBRARY_PATH=$OMPI_HOME/lib:$LD_LIBRARY_PATH
export OPAL_PREFIX=$OMPI_HOME

# ===== Allow root (IMPORTANT FIX) =====
export OMPI_ALLOW_RUN_AS_ROOT=1
export OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1

# ===== HPL Directory =====
cd /workspace/hpl-aocc/hpl-2.3/bin/AOCC

# ===== Runs =====

echo "Running 1 thread, 8 processes"
export OMP_NUM_THREADS=1
mpirun -np 8 ./xhpl > out_1t_8p.txt

echo "Running 2 threads, 4 processes"
export OMP_NUM_THREADS=2
mpirun -np 4 ./xhpl > out_2t_4p.txt

echo "Running 4 threads, 2 processes"
export OMP_NUM_THREADS=4
mpirun -np 2 ./xhpl > out_4t_2p.txt

echo "Running 8 threads, 1 process"
export OMP_NUM_THREADS=8
mpirun -np 1 ./xhpl > out_8t_1p.txt

echo "DONE"
