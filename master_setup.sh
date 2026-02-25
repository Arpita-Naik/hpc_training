#!/bin/bash

echo "===== HPC FRAMEWORK START ====="

# ---------------------------
# OS Detection
# ---------------------------
source system_check/detect_os.sh
echo "===== OS CHECK COMPLETE ====="

# ---------------------------
# Slurm Preprocess Check
# ---------------------------
source slurm/preprocess_slurm.sh
echo "--------------------------------"

# ---------------------------
# Slurm Decision Logic
# ---------------------------
if [ "$SLURM_STATUS" == "installed" ]; then
    echo "Slurm fully configured. Skipping installation."

elif [ "$SLURM_STATUS" == "needs_configuration" ]; then
    echo "Slurm exists but needs configuration."
    bash slurm/configure_slurm.sh

elif [ "$SLURM_STATUS" == "not_installed" ]; then
    echo "Slurm not installed."
    bash slurm/install_slurm.sh
    bash slurm/configure_slurm.sh

else
    echo "Unknown Slurm status."
    exit 1
fi

# ---------------------------
# GCC Setup
# ---------------------------
echo "Setting up GCC..."
bash modules/install_gcc_module.sh
echo "--------------------------------"

# ---------------------------
# Python Setup
# ---------------------------
echo "Setting up Python..."
bash modules/install_python_module.sh
echo "--------------------------------"

# ---------------------------
# OpenMPI Setup
# ---------------------------
echo "Setting up OpenMPI..."
bash modules/install_openmpi_module.sh
echo "--------------------------------"

echo "===== HPC FRAMEWORK SETUP COMPLETE ====="