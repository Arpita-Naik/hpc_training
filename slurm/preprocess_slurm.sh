#!/bin/bash

echo "Checking Slurm status..."

# Check if Slurm command exists
if command -v sinfo &> /dev/null; then
    echo "Slurm command found."

    # Check if slurmctld service exists
    if systemctl list-unit-files | grep -q slurmctld; then
        echo "Slurm service exists."

        # Check if running
        if systemctl is-active --quiet slurmctld; then
            echo "Slurm is running and properly installed."
            export SLURM_STATUS="installed"
        else
            echo "Slurm installed but not running."
            export SLURM_STATUS="needs_configuration"
        fi
    else
        echo "Slurm partially installed."
        export SLURM_STATUS="needs_configuration"
    fi
else
    echo "Slurm not installed."
    export SLURM_STATUS="not_installed"
fi