#!/bin/bash
#SBATCH --job-name=aocc_2x4
#SBATCH --output=aocc_2x4.out
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=4
#SBATCH --time=00:10:00

module purge
module load aocc/5.1.0
module load openmpi/5.0.9

cd ~/hpcg-3.1

export OMP_NUM_THREADS=4

mpirun -np 2 ./bin/xhpcg > run_aocc_2x4.txt
