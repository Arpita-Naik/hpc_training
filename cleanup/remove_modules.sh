#!/bin/bash

echo "Removing GCC and OpenMPI (optional)..."

read -p "Remove GCC and OpenMPI? (y/n): " choice

if [ "$choice" == "y" ]; then
    sudo apt remove gcc openmpi-bin libopenmpi-dev -y
else
    echo "Skipping compiler removal."
fi