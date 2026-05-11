#!/bin/bash
#SBATCH --job-name=hpcg_4x2
#SBATCH --output=hpcg_4x2.out
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=2
#SBATCH --time=00:10:00

module purge
module load compiler/2025.3.2
module load mpi/2021.17

cd ~/hpcg-3.1

export OMP_NUM_THREADS=2

mpirun -np 4 ./bin/xhpcg > run_4x2.txt
