#!/usr/bin/env bash

# Universal setup script for Termux and Debian-based systems

echo "Starting setup..."

# Check if running in Termux by checking for the termux-specific directory
if [[ -d "/data/data/com.termux/files/usr" ]]; then
    echo "Termux environment detected."
    pkg update -y
    pkg install python git python-pillow -y
    pip install -r requirements.txt
else
    echo "Standard Linux/VPS environment detected."

    # Check for sudo
    if [[ $EUID -ne 0 ]]; then
        SUDO="sudo"
    else
        SUDO=""
    fi

    # Use apt for package management on Debian-based systems
    $SUDO apt-get update -y
    $SUDO apt-get install -y python3 python3-pip git

    # Install python dependencies.
    # We add Pillow here because in Termux it's installed as a system package.
    pip3 install -r requirements.txt
    pip3 install Pillow
fi

echo "Setup complete."