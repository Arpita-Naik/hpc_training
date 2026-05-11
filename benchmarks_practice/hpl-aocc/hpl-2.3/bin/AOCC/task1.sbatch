#!/bin/bash
#SBATCH --job-name=hpl_aocc
#SBATCH --output=hpl_out.txt
#SBATCH --error=hpl_err.txt
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --time=00:10:00

module purge
module load aocc/5.1.0
module load aocl/5.2.0
module load openmpi/5.0.9

export LD_LIBRARY_PATH=/home/arpita/aocc-compiler-5.1.0/lib:$LD_LIBRARY_PATH
export OMP_NUM_THREADS=1

cd ~/hpl-aocc/hpl-2.3/bin/AOCC

mpirun --use-hwthread-cpus --bind-to core --cpu-set 0,2,4,6 -np 4 ./xhpl
