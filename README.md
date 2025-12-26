# Van UI - Camper Van Control System

A comprehensive control system for camper vans built on Raspberry Pi. This project provides a web-based dashboard and LLM-powered voice commands to control various van systems including the inverter, lights, LEDs, fan, and monitor battery status.

![Van UI Dashboard](https://github.com/user-attachments/assets/37672f85-7051-4777-aa6b-e53a8268ccfe)

## Overview

This system consists of three main components:

1. **Frontend Dashboard** - React-based web UI for monitoring and controlling van systems
2. **Backend API** - Flask server that interfaces with Raspberry Pi hardware (relays, sensors, LEDs)
3. **Voice Command App** - LLM-powered voice assistant using local Ollama for natural language command interpretation

### Use Case

Originally built to replace the need for an old phone + Victron mobile app (which doesn't work on newer iPhones) to control the inverter. The system has expanded to provide comprehensive van control through both a touchscreen interface and voice commands.

## Hardware Requirements

### Raspberry Pi
- Raspberry Pi (model 3B+ or newer recommended)
- Minimum 2GB RAM (4GB+ recommended for Ollama LLM)
- Raspberry Pi OS (latest version)

### Required Hardware Components

1. **Victron Smart Shunt** - Connected to Pi via USB/serial for battery monitoring
2. **5V Relay Module** - 1-channel relay connected to Victron MultiPlus inverter relay for toggling
3. **MPU6050 Sensor** - Accelerometer/gyroscope mounted inside van for level detection
4. **WS2812B LED Strip** - Addressable RGB LEDs controllable via GPIO
5. **USB Microphone** - For voice command input
6. **Speaker/Audio Output** - For TTS responses (can use Pi's audio jack or USB audio)
7. **Touchscreen Display** - For dashboard interface (optional, can access via network)

### GPIO Pin Configuration

- LED strip: GPIO 18 (PWM channel 0) - configured via `/boot/config.txt`
- Relay and sensor connections: See hardware module documentation

## Project Structure

```
van-ui/
├── frontend/          # React frontend application
│   ├── src/          # Source code
│   └── public/       # Static assets
├── backend/          # Flask API and voice app
│   ├── hardware/     # Hardware interface modules
│   ├── voice/        # Voice command system (LLM-powered)
│   ├── app.py        # Flask API server
│   └── voiceApp.py   # Voice command application
├── audio/            # Audio response files (legacy, now using TTS)
├── dist/             # Built frontend (generated)
└── README.md         # This file
```

## Initial Setup

### Prerequisites

- Raspberry Pi OS installed and updated
- Python 3.9+ installed
- Node.js 16+ and npm installed
- Internet connection for initial setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd van-ui
```

### 2. Frontend Setup

```bash
cd frontend/
npm install
npm run build
```

This creates the `dist/` folder that the Flask server will serve.

### 3. Backend Setup

```bash
cd backend/
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-pi.txt
```

### 4. Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
cd backend/
nano .env
```

Add the following variables:

```env
# Required: Picovoice access key for wake word detection
PICOVOICE_ACCESS_KEY=your_picovoice_key_here

# Optional: Voice command configuration
WAKE_WORD=jarvis
VOSK_MODEL_PATH=/home/steve/models/vosk/vosk-model-small-en-us-0.15

# Optional: API configuration
API_HOST=http://localhost:5000

# Optional: Ollama LLM configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b
CONFIDENCE_THRESHOLD=0.7

# Optional: TTS configuration
TTS_VOICE_ID=          # Leave empty for system default
TTS_RATE=150           # Words per minute
TTS_VOLUME=0.9         # 0.0 to 1.0
```

### 5. Vosk Speech Recognition Model

Download and extract the Vosk model:

```bash
# Create models directory
mkdir -p ~/models/vosk

# Download model (small English model recommended for Raspberry Pi)
cd ~/models/vosk
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip

# Update VOSK_MODEL_PATH in .env to match your path
```

### 6. Ollama Setup (for LLM Voice Commands)

The voice command system uses Ollama for local LLM-based command interpretation.

#### Install Ollama

```bash
# On Raspberry Pi
curl -fsSL https://ollama.com/install.sh | sh
```

#### Start Ollama Service

```bash
# Start Ollama (runs as a service)
ollama serve

# Or set up as systemd service
sudo systemctl enable ollama
sudo systemctl start ollama
```

#### Download Model

For Raspberry Pi, use a lightweight model:

```bash
# Recommended: Very small and fast (1B parameters, ~1GB RAM)
ollama pull llama3.2:1b

# Alternative: Small and efficient
ollama pull phi3:mini

# Larger option if Pi has 4GB+ RAM
ollama pull mistral:7b
```

The default model `llama3.2:1b` should work well on most Raspberry Pi 4 models with 2GB+ RAM.

#### Verify Ollama

```bash
# Test API is accessible
curl http://localhost:11434/api/tags

# Test model works
ollama run llama3.2:1b "Hello"
```

### 7. Hardware Configuration

#### Enable PWM for LEDs

Edit `/boot/config.txt`:

```bash
sudo nano /boot/config.txt
```

Add:

```
dtoverlay=ws281x,pin=18,channel=0
```

Reboot for changes to take effect.

## Running the Application

### Development Mode

#### Frontend Development

```bash
cd frontend/
npm start
```

#### Backend API Server

```bash
cd backend/
source venv/bin/activate
sudo python app.py
```

**Note:** The API server requires `sudo` because the LED controller needs root privileges.

#### Voice Command App

```bash
cd backend/
source venv/bin/activate
python voiceApp.py
```

**Note:** The voice app should NOT run with `sudo` as root doesn't have access to USB microphones.

### Production Deployment

See "Setup on PI" section below for systemd service configuration.

## Voice Command System

The voice command system uses:

1. **Wake Word Detection** - Porcupine (Picovoice) detects wake words ("jarvis", "terminator", "computer")
2. **Speech-to-Text** - Vosk converts speech to text
3. **Command Interpretation** - Local Ollama LLM interprets natural language commands
4. **Text-to-Speech** - pyttsx3 speaks responses back to the user
5. **Confidence-Based Confirmation** - Low-confidence commands require user confirmation

### How It Works

1. User says wake word → System activates
2. System greets user via TTS: "Yes?"
3. User speaks command → Vosk transcribes
4. LLM interprets command with confidence score
5. If confidence ≥ 0.7: Execute immediately with TTS feedback
6. If confidence < 0.7: Ask for confirmation via TTS, listen for yes/no
7. Execute command and provide TTS feedback

### Available Voice Commands

- **Toggle Inverter** - Turn inverter on/off
- **Toggle Fan** - Turn fan on/off
- **Toggle Lights** - Turn main lights on/off
- **Turn On LEDs** - Turn on LED strip with default color
- **Turn Off LEDs** - Turn off LED strip
- **Rainbow LEDs** - Set LED strip to rainbow animation
- **Blue LEDs** - Set LED strip to blue color

The LLM can understand natural language variations of these commands (e.g., "turn on the lights", "switch the inverter", "make the LEDs blue").

### Fallback Mode

If Ollama is unavailable, the system falls back to a hardcoded command mapping. This ensures voice commands continue to work even if the LLM service is down.

## API Endpoints

The Flask API provides the following endpoints:

### Inverter Control
- `GET /inverter` - Get inverter relay status
- `POST /inverter/toggle` - Toggle inverter on/off

### Fan Control
- `POST /fan/toggle` - Toggle fan on/off

### Lights Control
- `GET /lights` - Get lights relay status
- `POST /lights/toggle` - Toggle lights on/off

### LED Control
- `GET /leds` - Get LED status
- `POST /leds/configure` - Configure LEDs
  ```json
  {
    "on": true,
    "brightness": 70,
    "color": "255, 255, 255",
    "preset": "rainbow",
    "sleep": 5
  }
  ```

### Battery Monitoring
- `GET /smartshunt/data` - Get Victron SmartShunt data (voltage, current, amp hours, etc.)

### Level Sensor
- `GET /level_sensor/data` - Get MPU6050 level sensor data

### Application Control
- `POST /app/kill` - Kill Chromium browser (for kiosk mode)

## Setup on PI

### Create Systemd Services

Create services to run both applications on boot.

#### Van UI Service (API Server)

```bash
sudo nano /etc/systemd/system/van-ui.service
```

Add:

```ini
[Unit]
Description=Van UI
After=network.target

[Service]
WorkingDirectory=/home/steve/Desktop/van-ui
ExecStart=/home/steve/Desktop/van-ui/backend/venv/bin/python /home/steve/Desktop/van-ui/backend/app.py
StandardOutput=inherit
StandardError=inherit
Restart=always
User=root
Environment=NODE_ENV=production
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Note:** Replace `/home/steve` with your Pi username and adjust paths as needed.

#### Van Voice Service

```bash
sudo nano /etc/systemd/system/van-voice.service
```

Add:

```ini
[Unit]
Description=Van Voice App
After=sound.target ollama.service

[Service]
Environment="XDG_RUNTIME_DIR=/run/user/1000"
WorkingDirectory=/home/steve/Desktop/van-ui
ExecStartPre=/bin/sleep 5
ExecStart=/home/steve/Desktop/van-ui/backend/venv/bin/python /home/steve/Desktop/van-ui/backend/voiceApp.py
StandardOutput=journal
StandardError=journal
Restart=always
User=steve
Environment=NODE_ENV=production
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Note:** The voice service depends on `ollama.service` to ensure Ollama is running first.

#### Ollama Service (if not already installed)

Ollama typically installs its own systemd service. Verify it exists:

```bash
systemctl status ollama
```

If it doesn't exist, you may need to create one or ensure Ollama is set to start on boot.

#### Enable and Start Services

```bash
sudo systemctl daemon-reload
sudo systemctl enable van-ui
sudo systemctl enable van-voice
sudo systemctl enable ollama  # If needed
sudo systemctl start van-ui
sudo systemctl start van-voice
sudo systemctl start ollama   # If needed
```

#### Check Service Status

```bash
# View logs
journalctl -u van-ui.service -f
journalctl -u van-voice.service -f
journalctl -u ollama.service -f

# Check status
sudo systemctl status van-ui
sudo systemctl status van-voice
sudo systemctl status ollama
```

### Auto-launch Chromium Kiosk on Boot

Edit autostart config:

```bash
nano ~/.config/lxsession/LXDE-pi/autostart
```

Add:

```
@chromium-browser --noerrdialogs --kiosk http://172.20.10.6:5000 --incognito
```

**Note:** Replace the IP address with your Pi's IP address or use `http://localhost:5000`.

**Alternative:** If autostart doesn't work with your screen, create a desktop shortcut that runs the command manually.

To kill the browser:

```bash
pkill chromium
```

## Troubleshooting

### Voice App Not Responding

1. **Check Ollama is running:**
   ```bash
   systemctl status ollama
   curl http://localhost:11434/api/tags
   ```

2. **Check microphone permissions:**
   - Ensure voice app is NOT running as root
   - Check USB microphone is detected: `lsusb`

3. **Check logs:**
   ```bash
   journalctl -u van-voice.service -f
   ```

4. **Verify Vosk model path:**
   - Check `VOSK_MODEL_PATH` in `.env` matches actual model location

### Ollama Connection Issues

1. **Verify Ollama service:**
   ```bash
   systemctl status ollama
   ```

2. **Check model is downloaded:**
   ```bash
   ollama list
   ```

3. **Test API directly:**
   ```bash
   curl http://localhost:11434/api/chat -d '{"model": "llama3.2:1b", "messages": [{"role": "user", "content": "test"}]}'
   ```

4. **Check model name in config:**
   - Ensure `OLLAMA_MODEL` in `.env` matches downloaded model name

### TTS Not Working

1. **Check pyttsx3 installation:**
   ```bash
   python -c "import pyttsx3; print('OK')"
   ```

2. **Test TTS directly:**
   ```python
   import pyttsx3
   engine = pyttsx3.init()
   engine.say("Test")
   engine.runAndWait()
   ```

3. **Check audio output:**
   - Verify speaker/audio output is connected
   - Test with: `speaker-test -t sine -f 1000 -l 1`

### LED Strip Not Working

1. **Check GPIO configuration:**
   - Verify `/boot/config.txt` has `dtoverlay=ws281x,pin=18,channel=0`
   - Reboot after changes

2. **Check permissions:**
   - LED controller requires root/sudo
   - Ensure API server is running with sudo

3. **Check wiring:**
   - Verify LED strip is connected to GPIO 18
   - Check power supply is adequate

### API Not Accessible

1. **Check Flask server is running:**
   ```bash
   sudo systemctl status van-ui
   ```

2. **Check firewall:**
   ```bash
   sudo ufw status
   # If needed: sudo ufw allow 5000
   ```

3. **Check network:**
   - Verify Pi's IP address: `hostname -I`
   - Test locally: `curl http://localhost:5000`

### Frontend Not Loading

1. **Check dist folder exists:**
   ```bash
   ls -la dist/
   ```

2. **Rebuild frontend:**
   ```bash
   cd frontend/
   npm run build
   ```

3. **Check Flask is serving static files:**
   - Verify `app.py` has correct `static_folder` path

## Configuration Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PICOVOICE_ACCESS_KEY` | Yes | - | Picovoice API key for wake word detection |
| `WAKE_WORD` | No | `jarvis` | Primary wake word |
| `VOSK_MODEL_PATH` | No | `/home/steve/models/vosk/...` | Path to Vosk model |
| `API_HOST` | No | `http://localhost:5000` | Flask API URL |
| `OLLAMA_HOST` | No | `http://localhost:11434` | Ollama API URL |
| `OLLAMA_MODEL` | No | `llama3.2:1b` | Ollama model name |
| `CONFIDENCE_THRESHOLD` | No | `0.7` | Confidence threshold for confirmation |
| `TTS_VOICE_ID` | No | `None` | TTS voice ID (None = system default) |
| `TTS_RATE` | No | `150` | TTS speech rate (words per minute) |
| `TTS_VOLUME` | No | `0.9` | TTS volume (0.0 to 1.0) |

## Contributing

This is a personal project, but suggestions and improvements are welcome!

## License

[Add your license here]
