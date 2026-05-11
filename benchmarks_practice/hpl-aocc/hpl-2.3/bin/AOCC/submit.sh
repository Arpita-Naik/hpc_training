#!/bin/bash

echo "Submitting AOCC HPL jobs..."

sbatch run_aocc_omp1.sbatch
sbatch run_aocc_omp2.sbatch
sbatch run_aocc_omp4.sbatch
sbatch run_aocc_omp8.sbatch

echo "All AOCC jobs submitted!"
