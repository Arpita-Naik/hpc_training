#!/bin/bash
#SBATCH --job-name=stream_aocc
#SBATCH --output=stream_aocc_%j.out
#SBATCH --error=stream_aocc_%j.err
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --time=00:10:00

echo "===== STREAM AOCC Benchmark ====="
echo "Job ID: $SLURM_JOB_ID"
echo "Running on: $(hostname)"
echo "================================="
module purge
module load aocc/5.1.0 aocl/5.2.0
cd ~/STREAM/build_aocc
export OMP_NUM_THREADS=1
echo "Running STREAM with stride binding..."
srun --cpu-bind=map_cpu:0,2,4 ./stream_c.exe > res.txt

echo "Done"
