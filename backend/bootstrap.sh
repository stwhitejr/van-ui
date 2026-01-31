#!/bin/bash

echo "Setting up Pi environment..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-pi.txt

# Install Ollama (if not already installed)
if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "Ollama already installed"
fi

# Pull default model (if not already present)
echo "Checking for Ollama model..."
if ! ollama list | grep -q "llama3.2:1b"; then
    echo "Downloading llama3.2:1b model (this may take a while)..."
    ollama pull llama3.2:1b
else
    echo "Model llama3.2:1b already downloaded"
fi

# Install eSpeak-ng for TTS
if ! command -v espeak-ng &> /dev/null && ! command -v espeak &> /dev/null; then
    echo "Installing eSpeak-ng for TTS..."
    sudo apt-get update
    sudo apt-get install -y espeak-ng
else
    echo "eSpeak already installed"
fi

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Create .env file in backend/ directory (see README.md)"
echo "2. Download Vosk model (see README.md)"
echo "3. Configure /boot/config.txt for LEDs (see above)"
echo "4. Reboot if you modified /boot/config.txt"
