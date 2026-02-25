#!/bin/bash

echo "Detecting Operating System..."

if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "OS Name: $NAME"
    echo "OS Version: $VERSION_ID"

    case "$ID" in
        ubuntu|debian)
            echo "Package Manager: apt"
            export PKG_MANAGER="apt"
            ;;
        centos|rhel|fedora)
            echo "Package Manager: dnf/yum"
            export PKG_MANAGER="dnf"
            ;;
        *)
            echo "Unsupported OS"
            exit 1
            ;;
    esac
else
    echo "Cannot detect OS."
    exit 1
fi