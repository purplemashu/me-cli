#!/usr/bin/env bash
opkg update -y
opkg install python -y
opkg install python-pillow -y
pip install -r requirements.txt
