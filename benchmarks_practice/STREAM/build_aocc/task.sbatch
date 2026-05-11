#!/bin/bash
#SBATCH --job-name=half_socket_stride
#SBATCH --output=final_%j.out
#SBATCH --error=final_%j.err
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1

module purge
module load aocc/5.1.0 aocl/5.2.0

cd ~/STREAM/build_aocc

export OMP_NUM_THREADS=1

echo "Running on half socket with stride..."

# Run STREAM (example)
srun -n 4 --cpu-bind=map_cpu:0,2,4,6 ./stream_c.exe

echo "Done"
