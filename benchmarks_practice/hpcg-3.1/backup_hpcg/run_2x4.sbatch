#!/bin/bash
#SBATCH --job-name=hpcg_2x4
#SBATCH --output=hpcg_2x4.out
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=4
#SBATCH --time=00:30:00

module purge
module load compiler/2025.3.2
module load mpi/2021.17

cd ~/hpcg-3.1

export OMP_NUM_THREADS=4

mpirun -np 2 ./bin/xhpcg > run_2x4.txt
