# Settup up SpaceX-Launch-Bot & infoWebServer on a clean install of Ubuntu 16+

In all steps, SystemD files, and NGINX files replace `YOUR-USERNAME`, `SERVER-IP`, and `YOUR-TOKEN` with their corresponding values

## Steps in order:

SSH into your server as root, then execute the following commands (reading the comments as you go):

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

# Edit source/config/config.json with appopriate values
# Edit the files in /services with appropriate values 
# Edit the ini file in infoWebServer with appropriate values

$ sudo pip3 install -r requirements.txt
$ sudo cp -R services/systemd/. /lib/systemd/system/.
$ sudo chmod 644 /lib/systemd/system/SLB.service
$ sudo chmod 644 /lib/systemd/system/SLB-infoWebServer.service

# Actually enable and start the bot
# If you are using a previous data.pkl, MAKE SURE IT IS IN /resources BEFORE STARTING
$ sudo systemctl daemon-reload
$ sudo systemctl enable SLB
$ sudo systemctl start SLB

# Install web server stuff
$ sudo cp -R services/nginx/. /etc/nginx/sites-available/.
# Create a link so infoWebServer is enabled but also still in the available dir
$ sudo ln -s /etc/nginx/sites-available/infoWebServer /etc/nginx/sites-enabled
# Check for errors
$ sudo nginx -t

# Enable and start the log webserver
$ sudo systemctl enable SLB-infoWebServer
$ sudo systemctl start SLB-infoWebServer
# Make sure NGINX is allowed in our firewall
$ sudo ufw allow 'Nginx Full'
$ sudo systemctl restart nginx
```

## Misc

#### Disable & Stop:

```bash
sudo systemctl disable $ServiceName
sudo systemctl stop $ServiceName
```

#### Check status:

`systemctl status $ServiceName` *or* `journalctl -u $ServiceName`
