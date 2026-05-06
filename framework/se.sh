#!/bin/bash
#SBATCH --job-name=test_job
#SBATCH --output=output.txt
#SBATCH --error=error.txt
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:01:00

echo "Running on host: $(hostname)"
echo "Start time: $(date)"
sleep 20
echo "Finished!"



hpcg:
  problem:
    nx: 16
    ny: 16
    nz: 16
  runtime:
    ntasks: 1
    time: "00:05:00"

stream:
  runtime:
    threads: 1
