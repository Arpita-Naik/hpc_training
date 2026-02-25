#!/bin/bash

echo "===== GCC SETUP ====="

if command -v gcc &> /dev/null; then
    echo "GCC already installed."
    exit 0
fi

if [ "$PKG_MANAGER" == "apt" ]; then
    sudo apt update
    sudo apt install -y build-essential
elif [ "$PKG_MANAGER" == "dnf" ]; then
    sudo dnf install -y gcc gcc-c++ make
else
    echo "Unsupported package manager."
    exit 1
fi

echo "GCC installation complete."