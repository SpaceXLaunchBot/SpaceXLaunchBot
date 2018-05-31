# Settup up SpaceX-Launch-Bot & logServer on a clean install of Ubuntu 16+

In all steps (and SystemD files) replace `YOUR-USERNAME` and `YOUR-TOKEN` with their corresponding values

## Steps in order:

SSH into your server as the user you want to install this under (**not** root), then execute the following commands (reading the comments as you go):

(lines starting with `$` are showing a new command)

```bash
# Ubuntu & User setup
$ adduser YOUR-USERNAME
$ usermod -aG sudo YOUR-USERNAME
# Switch to user
$ su - YOUR-USERNAME
$ sudo apt update
$ sudo apt upgrade -y
$ sudo apt install git python3-pip nginx -y
$ mkdir ~/files && cd ~/files
# Start installing the actual bot
$ git clone https://github.com/r-spacex/SpaceX-Launch-Bot.git
$ cd SpaceX-Launch-Bot
# Edit SpaceX-Launch-Bot/source/config/config.json with appopriate values
$ nano source/config/config.json
$ pip3 install -r requirements.txt
# Edit the `.service` files in `/systemd` with appropriate values 
$ sudo cp -R systemd/. /lib/systemd/system/.
$ sudo chmod 644 /lib/systemd/system/SpaceX-Launch-Bot.service
$ sudo chmod 644 /lib/systemd/system/SPXLB-logServer.service
$ systemctl daemon-reload
$ systemctl enable SpaceX-Launch-Bot
$ systemctl start SpaceX-Launch-Bot
$ systemctl enable SPXLB-logServer
$ systemctl start SPXLB-logServer
```

## Misc

#### Disable & Stop:

```bash
systemctl disable $ServiceName
systemctl stop $ServiceName
```

#### Check status:

`systemctl status $ServiceName` *or* `journalctl -u $ServiceName`
