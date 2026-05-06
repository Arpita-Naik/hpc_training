#!/bin/bash
#SBATCH --job-name=hpcg_1x8
#SBATCH --output=hpcg_1x8.out
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=00:10:00

module purge
module load compiler/2025.3.2
module load mpi/2021.17

cd ~/hpcg-3.1

export OMP_NUM_THREADS=8

mpirun -np 1 ./bin/xhpcg > run_1x8.txt
