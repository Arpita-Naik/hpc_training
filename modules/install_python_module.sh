#!/bin/bash

echo "===== PYTHON SETUP ====="

if command -v python3 &> /dev/null; then
    echo "Python already installed."
else
    if [ "$PKG_MANAGER" == "apt" ]; then
        sudo apt install -y python3 python3-pip python3-venv
    elif [ "$PKG_MANAGER" == "dnf" ]; then
        sudo dnf install -y python3 python3-pip
    else
        echo "Unsupported package manager."
        exit 1
    fi
fi

# Create virtual environment
if [ ! -d "$HOME/hpc_python_env" ]; then
    python3 -m venv $HOME/hpc_python_env
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

echo "Python setup complete."