# Settup up SpaceX-Launch-Bot to run automatically on Ubuntu 16.x

Git clone this repo, pip3 install the requirements.txt, then:

run `sudo nano /lib/systemd/system/SpaceX-Launch-Bot.service`

insert contents:
```bash
[Unit]
Description=SpaceX-Launch-Bot Service
After=network.target
After=systemd-user-sessions.service
After=network-online.target

[Service]
# Env var
Environment="SpaceXLaunchBotToken=YOUR-TOKEN-HERE"
# Service stuff
User=YOUR-USER-NAME
Type=idle
# -u otherwise journal wont show print() output
ExecStart=/usr/bin/python3 -u /home/simon/files/SpaceX-Launch-Bot/source/main.py
Restart=always
RestartSec=10
StandardOutput=journal

[Install]
WantedBy=multi-user.target
```

Run:
```bash
sudo chmod 644 /lib/systemd/system/SpaceX-Launch-Bot.service
sudo systemctl daemon-reload
sudo systemctl enable SpaceX-Launch-Bot.service
sudo systemctl start SpaceX-Launch-Bot.service
```

Disable / Stop:

`sudo systemctl disable SpaceX-Launch-Bot.service`
`sudo systemctl stop SpaceX-Launch-Bot.service`

How to check the status:

`sudo systemctl status SpaceX-Launch-Bot.service`

See program output:

`journalctl -u SpaceX-Launch-Bot`
