function askyn {
    while true; do
        read -p "$1 [Yy/Nn]" yn
        case $yn in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer y or n";;
        esac
    done
}

echo "This script will erase your current redis config if you have one"
echo "For this script to work, these things need to be true:"
echo "SLB should exist in /opt/SpaceX-Launch-Bot"
echo "pip3 should be installed"
echo "You have a Discord bot token and a Discord-bot-list token for that bot"

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
askyn "Skip editing SLB.service? This will have to be done before running it" || sudo nano /etc/systemd/system/SLB.service

echo "Copying redis config to /etc/redis"
sudo cp -R services/redis/. /etc/redis
echo "Restarting Redis"
sudo systemctl restart redis

askyn "Skip editing config.json?" || sudo nano /opt/SpaceX-Launch-Bot/source/config/config.json

echo ""
echo "Setup finished"
echo "If you have a dump.rdb, stop redis, move it to /var/lib/redis and then start it again"
echo "To start SLB enable and start it using systemd"
echo ""
