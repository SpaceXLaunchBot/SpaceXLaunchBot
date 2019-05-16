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
    - The latest version of Redis from apt
    - The latest version of pip for python3
Make sure:
    - Python 3.6+ exists under the "python3" command
    - The SLB files exist in /opt/SpaceX-Launch-Bot
    - You have a Discord bot token
    - You have a Discord-bot-list token
EndOfMsg

askyn "Is this correct?" || exit

echo "Installing apt dependencies"
sudo apt install python3-distutils redis-server -y

cd /tmp

echo "Installing pip for Python3"
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py
rm get-pip.py

cd /opt/SpaceX-Launch-Bot

echo "Setting correct owner and permissions for /opt/SpaceX-Launch-Bot"
sudo adduser --system --group --no-create-home slb
sudo chown -R slb:slb /opt/SpaceX-Launch-Bot
sudo chmod -R u+rwX,go+rX,go-w /opt/SpaceX-Launch-Bot

echo "Setting up /var/log/SLB"
sudo mkdir /var/log/slb
sudo chown slb:slb /var/log/slb

echo "Install Python3 requirements through pip3"
sudo pip3 install -r requirements.txt

echo "Copying over systemd file(s)"
sudo cp -R -p services/systemd/. /etc/systemd/system

echo "Copying redis config to /etc/redis"
sudo cp -R services/redis/. /etc/redis
echo "Restarting Redis"
sudo systemctl restart redis

if askyn "Edit slb.service now? This will have to be done before running it";
then sudo nano /etc/systemd/system/slb.service; fi

cat << EndOfMsg

Setup finished
If you have a dump.rdb, stop redis, move it to /var/lib/redis and then start it again"
To start SLB enable and start it using systemd

EndOfMsg

# To get a copy of dump.rdb:
# sudo cp /var/lib/redis/dump.rdb ~/
# sudo chwon USER dump.rdb
# --> Download from server
