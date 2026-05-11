#!/bin/bash
#SBATCH --job-name=aocc_4x2
#SBATCH --output=aocc_4x2.out
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=2
#SBATCH --time=00:20:00

module purge
module load aocc/5.1.0
module load openmpi/5.0.9

cd ~/hpcg-3.1

export OMP_NUM_THREADS=2

mpirun -np 4 ./bin/xhpcg > run_aocc_4x2.txt
