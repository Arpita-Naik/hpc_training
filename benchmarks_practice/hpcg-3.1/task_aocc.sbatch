#!/bin/bash
#SBATCH --job-name=hpcg_intel
#SBATCH --output=hpcg_out.txt
#SBATCH --error=hpcg_err.txt
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --time=00:10:00

module purge
module load compiler/2025.3.2
module load mpi/2021.17
module load mkl/2025.3

export OMP_NUM_THREADS=1
export I_MPI_PIN=1
export I_MPI_PIN_DOMAIN=socket
export I_MPI_PIN_ORDER=compact
export I_MPI_PIN_PROCESSOR_LIST=0,2,4,6

export I_MPI_DEBUG=5
export I_MPI_FABRICS=shm

cd ~/hpcg-3.1/bin

mpirun -bootstrap fork -np 4 ./xhpcg
