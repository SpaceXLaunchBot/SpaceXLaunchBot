# Using Systemd to run automatically

Systemd file location: `/lib/systemd/system/SpaceX-Launch-Bot.service`

Setup:

Git clone this repo, pip3 install the requirements.txt, then:

Edit the system wide env file:

`sudo -H nano /etc/environment`

Insert the `SpaceXLaunchBotToken` env variable on a new line:

`SpaceXLaunchBotToken="your-token"`

Create file & insert contents:
```shell
[Unit]
Description=SpaceX-Launch-Bot Service
After=multi-user.target

[Service]
Type=idle
ExecStart=/usr/bin/python3 /home/simon/files/SpaceX-Launch-Bot/source/main.py > /home/simon/files/SpaceX-Launch-Bot/source/main.log 2>&1
Restart=always
RestartSec=3
```

Run:
```shell
sudo chmod 644 /lib/systemd/system/SpaceX-Launch-Bot.service
sudo systemctl daemon-reload
sudo systemctl enable SpaceX-Launch-Bot.service
sudo reboot
```

Disable / Stop:

`sudo systemctl enable SpaceX-Launch-Bot.service`

How to check the status:

`sudo systemctl status SpaceX-Launch-Bot.service`
