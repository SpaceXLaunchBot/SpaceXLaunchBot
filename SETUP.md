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
$ sudo apt install git nginx -y
$ mkdir ~/files && cd ~/files

# Install pip the proper way
# https://pip.pypa.io/en/stable/installing/
$ wget https://bootstrap.pypa.io/get-pip.py
$ sudo python3 get-pip.py
$ rm get-pip.py

# Start installing the actual bot
$ git clone https://github.com/r-spacex/SpaceX-Launch-Bot.git
$ cd SpaceX-Launch-Bot
# Edit SpaceX-Launch-Bot/source/config/config.json with appopriate values
$ nano source/config/config.json
$ sudo pip3 install -r requirements.txt
# Edit the `.service` files in `/systemd` with appropriate values 
$ sudo cp -R services/systemd/. /lib/systemd/system/.
$ sudo chmod 644 /lib/systemd/system/SpaceX-Launch-Bot.service
$ sudo chmod 644 /lib/systemd/system/SPXLB-logServer.service

# Actually enable and start the bot
# If you are using a previous data.pkl, MAKE SURE IT IS IN /resources BEFORE STARTING
$ sudo systemctl daemon-reload
$ sudo systemctl enable SpaceX-Launch-Bot
$ sudo systemctl start SpaceX-Launch-Bot

# Install web server stuff
$ sudo cp -R services/nginx/. /etc/nginx/sites-available/.
$ sudo ln -s /etc/nginx/sites-available/logServer /etc/nginx/sites-enabled
# Check for errors
$ sudo nginx -t

# Enable and start the log webserver
$ sudo systemctl restart nginx
$ sudo ufw allow 'Nginx Full'
$ sudo systemctl enable SPXLB-logServer
$ sudo systemctl start SPXLB-logServer
```

## Misc

#### Disable & Stop:

```bash
sudo systemctl disable $ServiceName
sudo systemctl stop $ServiceName
```

#### Check status:

`systemctl status $ServiceName` *or* `journalctl -u $ServiceName`
