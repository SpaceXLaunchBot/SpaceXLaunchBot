echo "This script will erase your current redis config if you have one"
echo "For this script to work, these things need to be true:"
echo "SLB should exist in /opt/SpaceX-Launch-Bot"
echo "pip3 should be installed"
echo "You have a Discord bot token and a Discord-bot-list token for that bot"
while true; do
    read -p "Is this correct? [Yy/Nn]" yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) exit;;
        * ) echo "Please answer y or n";;
    esac
done

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
while true; do
    read -p "Edit SLB.service now? This will have to be done before running it [Yy/Nn]" yn
    case $yn in
        [Yy]* ) sudo nano /etc/systemd/system/SLB.service; break;;
        [Nn]* ) break;;
        * ) echo "Please answer y or n";;
    esac
done

echo "Copying redis config to /etc/redis"
sudo cp -R services/redis/. /etc/redis
echo "Restarting Redis"
sudo systemctl restart redis

while true; do
    read -p "Fill out config.json now? [Yy/Nn]" yn
    case $yn in
        [Yy]* ) sudo nano /opt/SpaceX-Launch-Bot/source/config/config.json; break;;
        [Nn]* ) break;;
        * ) echo "Please answer y or n";;
    esac
done

echo ""
echo "Setup finished"
echo "If you have a dump.rdb, stop redis, move it to /var/lib/redis and then start it again"
echo "To start SLB enable and start it using systemd"
echo ""
