#!/bin/bash

echo "===== OPENMPI SETUP ====="

if command -v mpirun &> /dev/null; then
    echo "OpenMPI already installed."
    exit 0
fi

if [ "$PKG_MANAGER" == "apt" ]; then
    sudo apt install -y openmpi-bin libopenmpi-dev
elif [ "$PKG_MANAGER" == "dnf" ]; then
    sudo dnf install -y openmpi openmpi-devel
else
    echo "Unsupported package manager."
    exit 1
fi

echo "OpenMPI installation complete."