#!/bin/bash

echo "Setting up Pi environment..."

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-pi.txt

# Enable PWM audio
sudo nano /boot/config.txt
dtoverlay=ws281x,pin=18,channel=0

echo "Setup complete."
