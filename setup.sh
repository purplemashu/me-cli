#!/usr/bin/env bash
pkg update && pkg upgrade -y
pkg install git -y
pkg install python -y
pkg install python-pillow -y
git clone https://github.com/purplemashu/me-cli
cd me-cli
pip install -r requirements.txt
python main.py
