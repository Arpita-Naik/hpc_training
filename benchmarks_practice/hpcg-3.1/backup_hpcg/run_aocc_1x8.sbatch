#!/bin/bash
#SBATCH --job-name=aocc_1x8
#SBATCH --output=aocc_1x8.out
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=00:10:00

module purge
module load aocc/5.1.0
module load openmpi/5.0.9

cd ~/hpcg-3.1

export OMP_NUM_THREADS=8

mpirun -np 1 ./bin/xhpcg > run_aocc_1x8.txt
