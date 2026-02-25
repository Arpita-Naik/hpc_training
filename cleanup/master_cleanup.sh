#!/bin/bash

echo "===== HPC CLEANUP START ====="

bash cleanup/remove_python_env.sh
bash cleanup/remove_modules.sh
bash cleanup/remove_slurm.sh

echo "===== CLEANUP COMPLETE ====="