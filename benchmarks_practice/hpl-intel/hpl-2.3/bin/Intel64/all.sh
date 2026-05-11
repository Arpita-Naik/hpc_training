#!/bin/bash

echo "Submitting all HPL jobs..."

sbatch run_omp1.sbatch
sbatch run_omp2.sbatch
sbatch run_omp4.sbatch
sbatch run_omp8.sbatch

echo "All jobs submitted!"
