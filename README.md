# My Van Dashboard
This dashboard assumes the following:
1. You're using this on a raspberry pi
2. You've connected a victron smart shunt to the pi
3. You've connected a 1 channel 5v relay to the victron multiplus inverter relay for toggling on and off
4. You have a MPU6050 sensor mounted inside the van and hooked up the PI
5. You have a screen hooked up the PI (Can also be accessed on local network via IP address and port)

This dashboard gives us:
1. Victron smartshunt data like battery voltage, current, consumed amp hours, etc
2. How out of the level the vehicle currently is. Good for checking sleep quality.
3. An ability to easily toggle on the inverter without manually flipping the inverter switch.


## Setup

### Create a boot script on the PI
Assuming you want this to run on boot.


Create `~/startup.sh:`
```bash
#!/bin/bash

sudo /home/pi/van-ui/backend/venv/bin/python /home/pi/van-ui/backend/app.py &
```

Make it executable `chmod +x ~/startup.sh`

### Create a systemd service
`sudo nano /etc/systemd/system/van-ui.service`

Add to file
```
[Unit]
Description=Van Dashboard Startup
After=network.target

[Service]
ExecStart=/bin/bash /home/pi/startup.sh
WorkingDirectory=/home/pi/van-ui
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

Run:
```
sudo systemctl enable van-ui
sudo systemctl start van-ui
```

### Auto-launch Chromium kiosk on boot

Edit autostart config
`nano ~/.config/lxsession/LXDE-pi/autostart`
Add:
`@chromium-browser --noerrdialogs --kiosk http://172.20.10.6:5000 --incognito --ignore-certificate-errors`

Modify the URL above as needed.


