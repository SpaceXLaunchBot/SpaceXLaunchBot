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
This script will erase your current redis config if you have one
For this script to work, these things need to be true:
SLB should exist in /opt/SpaceX-Launch-Bot
pip3 should be installed
You have a Discord bot token and a Discord-bot-list token for that bot
EndOfMsg

askyn "Is this correct?" || exit

echo "Installing apt dependencies"
sudo apt install redis-server -y

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
if askyn "Edit SLB.service now? This will have to be done before running it";
then sudo nano /etc/systemd/system/SLB.service; fi

echo "Copying redis config to /etc/redis"
sudo cp -R services/redis/. /etc/redis
echo "Restarting Redis"
sudo systemctl restart redis

if askyn "Edit config.json now?";
then sudo nano /opt/SpaceX-Launch-Bot/source/config/config.json; fi

cat << EndOfMsg

Setup finished
If you have a dump.rdb, stop redis, move it to /var/lib/redis and then start it again"
To start SLB enable and start it using systemd"

EndOfMsg
