# My Van UI
This UI assumes the following:
1. You're using this on a raspberry pi
2. You've connected a victron smart shunt to the pi
3. You've connected a 1 channel 5v relay to the victron multiplus inverter relay for toggling on and off
4. You have a MPU6050 sensor mounted inside the van and hooked up the PI
5. You have a screen hooked up the PI (Can also be accessed on local network via IP address and port)
6. You have WS2812B LEDs controllable by the PI
7. You have a USB microphone plugged into the PI

This UI gives us:
1. Victron smartshunt data like battery voltage, current, consumed amp hours, etc
2. How out of the level the vehicle currently is. Good for checking sleep quality.
3. An ability to easily toggle on the inverter without manually flipping the inverter switch.
4. Control for the LEDs including color, brightness, sleep, and some animation presets.
5. Voice commands to toggle the inverter and change lights.

## Running

### Frontend

This will output a `dist/` folder at the root of the project. The `backend/app.py` will use this to serve the frontend.

```bash
cd frontend/
npm install
npm run build
```


### Backend / Scripts

We have 2 separate apps for the main flask/api app and the voice command app. This is because the LED package we're using requires `sudo` while the voice stuff can't use `sudo` as root doesn't have access to the USB mic.

Run flask web server and API
```bash
cd backend/
sudo python app.py
```

Run voice app
```bash
cd backend/
python voiceApp.py
```

See `backend/hardware/voice.py` for available commands.


## Setup on PI

### Create a boot script on the PI for each python app

Assuming you want this to run on boot.


### Create a systemd service

Swap `steve` with your pi username.

`sudo nano /etc/systemd/system/van-ui.service`

Add to file
```
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

`sudo nano /etc/systemd/system/van-voice.service`

Add to file
```
[Unit]
Description=Van Voice App
After=sound.target

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

Run:
```
sudo systemctl daemon-reexec
sudo systemctl enable van-ui
sudo systemctl start van-ui
sudo systemctl enable van-voice
sudo systemctl start van-voice
```

#### Check logs

```bash
journalctl -u van-ui.service -f
journalctl -u van-voice.service -f
```

### Auto-launch Chromium kiosk on boot

*Note* I could not get this to work with my PI screen so i just made a desktop button that i can click on the pi screen that runs the below command. Maybe the autostart will work for your screen type.

Edit autostart config
`nano ~/.config/lxsession/LXDE-pi/autostart`

Add:
`@chromium-browser --noerrdialogs --kiosk http://172.20.10.6:5000 --incognito`

Modify the URL above as needed.

If you need to kill the browser use `pkill chromium`


