#!/bin/bash

if command -v sinfo &> /dev/null; then
    read -p "Slurm detected. Remove Slurm? (y/n): " choice

    if [ "$choice" == "y" ]; then
        sudo apt remove slurm-wlm -y
    else
        echo "Skipping Slurm removal."
    fi
else
    echo "Slurm not installed."
fi