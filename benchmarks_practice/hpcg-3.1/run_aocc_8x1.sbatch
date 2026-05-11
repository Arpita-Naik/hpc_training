#!/bin/bash
#SBATCH --job-name=aocc_8x1
#SBATCH --output=aocc_8x1.out
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --time=00:20:00

module purge
module load aocc/5.1.0
module load openmpi/5.0.9

cd ~/hpcg-3.1

export OMP_NUM_THREADS=1

mpirun -np 8 ./bin/xhpcg > run_aocc_8x1.txt
