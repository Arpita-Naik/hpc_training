#!/bin/bash
#SBATCH --job-name=stream_aocc
#SBATCH --output=stream_aocc_%j.out
#SBATCH --error=stream_aocc_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=00:10:00

echo "===== STREAM AOCC Benchmark ====="
echo "Job ID: $SLURM_JOB_ID"
echo "Running on: $(hostname)"
echo "================================="
module purge
module load aocc/5.1.0 aocl/5.2.0

cd ~/STREAM/build_aocc

echo "Modules loaded:"
module list

for t in 1 2 4 8
do
    echo " Running with OMP_NUM_THREADS=$t "
    export OMP_NUM_THREADS=$t
    export OMP_PROC_BIND=spread
    export OMP_PLACES=cores

    ../stream_c.exe
done


