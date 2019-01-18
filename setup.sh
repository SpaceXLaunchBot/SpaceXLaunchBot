# Installs SLB and all of its dependencies
# TODO: https://askubuntu.com/questions/868848/how-to-install-redis-on-ubuntu-16-04
    # - Create dystemd file for Redis and move it to correct location
    # - Use new Redis v5 config

askyn() {
    while true; do
        read -p "$1 [Yy/Nn]" yn
        case $yn in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer y or n";;
        esac
    done
}

cat << EndOfMsg
This script will install these dependenies:
    - The latest stable version of Redis
    - The latest version of pip for python3
Make sure:
    - Python 3.6+ exists under the "python3" command
    - The SLB files exist in /opt/SpaceX-Launch-Bot
    - You have a Discord bot token
    - You have a Discord-bot-list token
EndOfMsg

askyn "Proceed with the installation?" || exit

echo "Updating & Upgrading apt"
sudo apt update
sudo apt upgrade -y

echo "Installing apt dependecies"
sudo apt install python3-distutils build-essential tcl make -y

cd /tmp

echo "Installing latest stable version of Redis"
curl -O http://download.redis.io/redis-stable.tar.gz
tar xzvf redis-stable.tar.gz
cd redis-stable
make
make test
cat << EndOfMsg

make test for Redis is done
If this failed, stop this script using ctrl-c and fix the error(s)
Then run this script again
EndOfMsg
read -rsp "Otherwise, press enter to continue"
sudo make install
cd ..
# Below is from https://askubuntu.com/a/868862
# Redis config directory
sudo mkdir /etc/redis
# Create redis user and group with same ID but no home directory
sudo adduser --system --group --no-create-home redis   
sudo mkdir /var/lib/redis
sudo chown redis:redis /var/lib/redis
sudo chmod 770 /var/lib/redis

echo "Installing pip for Python3"
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py
rm get-pip.py

cd /opt/SpaceX-Launch-Bot

echo "Setting correct owner and permissions for /opt/SpaceX-Launch-Bot"
sudo adduser --system --group --no-create-home SLB
sudo chown -R SLB:SLB /opt/SpaceX-Launch-Bot
sudo chmod -R u+rwX,go+rX,go-w /opt/SpaceX-Launch-Bot

echo "Setting up /var/log/SLB"
sudo mkdir /var/log/SLB
sudo chown SLB:SLB /var/log/SLB

echo "Install Python3 requirements through pip3"
sudo pip3 install -r requirements.txt

echo "Copying over systemd file(s)"
sudo cp -R -p services/systemd/. /etc/systemd/system

echo "Copying redis config to /etc/redis"
sudo cp -R services/redis/. /etc/redis
echo "Starting / restarting Redis"
sudo systemctl enable redis
# restart will start it if not running already
sudo systemctl restart redis

if askyn "Edit SLB.service now? This will have to be done before running it";
then sudo nano /etc/systemd/system/SLB.service; fi

cat << EndOfMsg

Setup finished
If you have a dump.rdb, stop redis, move it to /var/lib/redis and then start it again"
To start SLB enable and start it using systemd"

EndOfMsg
