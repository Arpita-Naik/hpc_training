#!/bin/bash
#SBATCH --job-name=stream_intel
#SBATCH --output=stream_intel_%j.out
#SBATCH --error=stream_intel_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=00:10:00

echo "===== STREAM INTEL Benchmark ====="
echo "Job ID: $SLURM_JOB_ID"
echo "Running on: $(hostname)"
module purge
module load compiler-intel-llvm/2025.3.2
cd ~/STREAM/build_intel

module list

for t in 1 2 4 8
do
    echo ""
    echo "===== Running with OMP_NUM_THREADS=$t ====="
    export OMP_NUM_THREADS=$t
    ./stream_c.exe
done
