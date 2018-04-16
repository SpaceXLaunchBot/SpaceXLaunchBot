# Using Systemd to run automatically

File location: `/lib/systemd/system/SpaceX-Launch-Bot.service`

Setup:

Edit the system wide env file:

`sudo -H gedit /etc/environment`

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
```

Run:
```shell
sudo chmod 644 /lib/systemd/system/SpaceX-Launch-Bot.service
sudo systemctl daemon-reload
sudo systemctl enable SpaceX-Launch-Bot.service
sudo reboot
```

How to check the status:

`sudo systemctl status SpaceX-Launch-Bot.service`
