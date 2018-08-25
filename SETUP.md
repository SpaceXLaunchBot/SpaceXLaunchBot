# Setup

This guide will install SpaceX-Launch-Bot and the accompanying web server on a clean install of Ubuntu 16+

## Instructions

SSH into your server as root, then execute the commands in the steps below. The commands are split into sections but should all be executed in order

### User setup

```bash
# Setup your username (for example: user1)
$ adduser YOUR-USERNAME
# We want to be able to use sudo
$ usermod -aG sudo YOUR-USERNAME

# Switch to your user
$ su - YOUR-USERNAME

# SLB stands for SpaceX-Launch-Bot
$ sudo adduser --system --group --no-create-home SLB
$ sudo adduser --system --group --no-create-home redis

# We want to be able to update SLB files manually
$ usermod -aG SLB YOUR-USERNAME
```

### Update and upgrade

```bash
$ sudo apt update
$ sudo apt upgrade -y
```

### Dissalow root login

```bash
sudo nano /etc/ssh/sshd_config
```

Find the following line:

`# PermitRootLogin yes`

Change it to "no" and un-comment (if it isn't already)

`PermitRootLogin no`

Restart the SSHD service

```bash
service sshd restart
```

### Install things

What these programs are for (reused programs are not repeated):

- `git` for Github cloning

- `fail2ban` for security

- `nginx` acts as a reverse proxy for webServer

- `python3-distutils` for `get-pip`

- `gcc` and `python3-dev` to build `uWSGI`

- `make`, and `tcl` for building Redis & running tests

```bash
$ sudo apt install git fail2ban nginx python3-distutils python3-dev gcc make tcl -y

# Install Digital Ocean monitoring (if using DO as hosting)
$ curl -sSL https://agent.digitalocean.com/install.sh | sh
```

### Set up ufw (a firewall)

```bash
# Make sure SSH connections are allowed in the firewall
$ sudo ufw allow ssh
# Make sure NGINX HTTP connections are allowed
$ sudo ufw allow 'Nginx HTTP'
# Turn on the firewall (you may need to reconnect)
$ sudo ufw enable
```

### Install and run netdata
```bash
bash <(curl -Ss https://my-netdata.io/kickstart.sh)
```

### Install Redis

```bash
$ cd /tmp
$ curl -O http://download.redis.io/redis-stable.tar.gz
$ tar xzvf redis-stable.tar.gz
$ cd redis-stable
$ make
$ make test
$ sudo make install
$ cd ..
$ rm -rf redis-stable redis-stable.tar.gz
```

### Setup Redis

```bash
# For putting Redis .conf file(s) in
$ sudo mkdir /etc/redis

# This is where we dump the DB to 
$ sudo mkdir /var/lib/redis
$ sudo chown redis:redis /var/lib/redis
$ sudo chmod 770 /var/lib/redis
```

### Install pip

```bash
# Install pip the proper way
# https://pip.pypa.io/en/stable/installing/
$ wget https://bootstrap.pypa.io/get-pip.py
$ sudo python3 get-pip.py
$ rm get-pip.py
```

### Clone SpaceX-Launch-Bot

The bot is "installed" to `/opt`

```bash
$ cd /opt
$ sudo git clone https://github.com/r-spacex/SpaceX-Launch-Bot.git
$ cd SpaceX-Launch-Bot
```

### Config

Now you can edit `source/config/config.json` with your chosen settings

```bash
# Setup permissions
$ sudo chown -R SLB:SLB /opt/SpaceX-Launch-Bot
# https://superuser.com/a/91966
$ sudo chmod -R u+rwX,go+rX,go-w SpaceX-Launch-Bot/
$ sudo chmod 0774 /opt/SpaceX-Launch-Bot/scripts/*.sh

# Create log directory
$ sudo mkdir /var/log/SLB
$ sudo chown SLB /var/log/SLB
```

### Setup SpaceX-Launch-Bot

```bash
$ sudo pip3 install -r requirements.txt
$ sudo python3 setup.py
```

### Setup services and system files

```bash
# Everyone can read the services, only current user can write
$ sudo chmod -R 644 services/systemd

# Copy systemd files over (-p preserves the perms we just set)
$ sudo cp -R -p services/systemd/. /lib/systemd/system/.

# Copy Redis stuff over
$ sudo cp -R services/redis/. /etc/redis

# Copy netdata stuff over
$ sudo cp -R services/netdata/. /opt/netdata/etc/netdata
```

### Setup the web server(s)

```bash
$ sudo cp -R services/nginx/. /etc/nginx/sites-available/.
# Create a link so the web server is enabled but also still in the available dir
$ sudo ln -s /etc/nginx/sites-available/SLB-webServer /etc/nginx/sites-enabled
$ sudo ln -s /etc/nginx/sites-available/netdata-webServer /etc/nginx/sites-enabled
$ sudo ln -s /etc/nginx/sites-available/SLB-webServer-status /etc/nginx/sites-enabled
```

### Move fail2ban config to correct directory

```bash
$ sudo cp -R services/fail2ban/. /etc/fail2ban/.
```

### Before starting everything

- If you are re-using a previously dumped Redis database, remember to load it up now

### Set scripts to be executable and boot everything up

```bash
$ sudo chmod +x -R scripts
$ cd scripts
$ ./startAll
```

## Misc commands

#### Check the status of a service:

```bash
$ systemctl status $serviceName.service
# or
$ journalctl -u $serviceName.service
# or
$ service $serviceName.service status
```
