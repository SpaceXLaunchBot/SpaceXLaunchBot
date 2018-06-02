# Settup up SpaceX-Launch-Bot & infoWebServer on a clean install of Ubuntu 16+

In all steps replace `YOUR-USERNAME` with the username that the service(s) will be run under

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

# distutils because get-pip needs it
# gcc & python3-dev because uWSGI needs them to build
# make & tcl for building redis & running tests
$ sudo apt install git nginx python3-distutils python3-dev gcc make tcl -y

# Install Digital Ocean monitoring (if using DO as hosting)
$ curl -sSL https://agent.digitalocean.com/install.sh | sh

# Make sure SSH connections are allowed in the firewall
$ sudo ufw allow ssh
# Make sure NGINX HTTP connections are allowed
$ sudo ufw allow 'Nginx HTTP'
# Turn on the firewall (you may need to reconnect)
$ sudo ufw enable

# Install Redis
$ cd /tmp
$ curl -O http://download.redis.io/redis-stable.tar.gz
$ tar xzvf redis-stable.tar.gz
$ cd redis-stable
$ make
$ make test
$ sudo make install
$ cd .. && rm -rf redis-stable

# For putting Redis .conf file(s) in
$ sudo mkdir /etc/redis

# Set Redis user
$ sudo adduser --system --group --no-create-home redis

# This is where we dump the DB to 
$ sudo mkdir /var/lib/redis
$ sudo chown redis:redis /var/lib/redis

# Regular users should not be able to access this location
$ sudo chmod 770 /var/lib/redis

# We "install" the bot to /opt
$ cd /opt

# Install pip the proper way
# https://pip.pypa.io/en/stable/installing/
$ wget https://bootstrap.pypa.io/get-pip.py
$ sudo python3 get-pip.py
$ rm get-pip.py

# Start installing the actual bot
$ git clone https://github.com/r-spacex/SpaceX-Launch-Bot.git
$ cd SpaceX-Launch-Bot

# Now you can edit source/config/config.json with your chosen settings

$ sudo pip3 install -r requirements.txt
$ python3 setup.py

# Everyone can read the services, only current user can write
$ sudo chmod -R 644 services/systemd

# Copy systemd files over (-p preserves the perms we just set)
$ sudo cp -R -p services/systemd/. /lib/systemd/system/.

# Copy Redis stuff over
$ sudo cp -R services/redis/. /etc/redis

# Install web server stuff
$ sudo cp -R services/nginx/. /etc/nginx/sites-available/.
# Create a link so infoWebServer is enabled but also still in the available dir
$ sudo ln -s /etc/nginx/sites-available/infoWebServer /etc/nginx/sites-enabled

# Set scripts to be executable and boot everything up
$ sudo chmod +x -R scripts
$ cd scripts
$ ./startAll
```

## Misc

#### Check status:

```bash
$ systemctl status $serviceName.service
# or
$ journalctl -u $serviceName.service
# or
$ service $serviceName.service status
```
