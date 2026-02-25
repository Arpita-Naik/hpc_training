#!/bin/bash

echo "===== INSTALLING SLURM & MUNGE ====="

if [ "$PKG_MANAGER" == "apt" ]; then
    echo "Detected Debian/Ubuntu system"

    sudo apt update
    sudo apt install -y slurm-wlm munge

elif [ "$PKG_MANAGER" == "dnf" ]; then
    echo "Detected RHEL/Fedora system"

    sudo dnf install -y slurm slurm-slurmd slurm-slurmctld munge munge-libs munge-devel

else
    echo "Unsupported package manager."
    exit 1
fi

echo "Installation complete."