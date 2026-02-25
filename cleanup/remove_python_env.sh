#!/bin/bash

if [ -d "$HOME/hpc_python_env" ]; then
    echo "Removing Python virtual environment..."
    rm -rf $HOME/hpc_python_env
else
    echo "No Python virtual environment found."
fi