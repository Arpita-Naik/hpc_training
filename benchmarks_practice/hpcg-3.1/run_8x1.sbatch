#!/bin/bash
#SBATCH --job-name=hpcg_8x1
#SBATCH --output=hpcg_8x1.out
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --time=00:10:00

module purge
module load compiler/2025.3.2
module load mpi/2021.17

cd ~/hpcg-3.1

export OMP_NUM_THREADS=1

mpirun -np 8 ./bin/xhpcg > run_8x1.txt
