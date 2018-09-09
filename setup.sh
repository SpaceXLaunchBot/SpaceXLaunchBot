echo "For this script to work, these things need to be true:"
echo "SLB should exist in /opt/SpaceX-Launch-Bot"
echo "pip3 should be installed"
echo "You have your Discord bot token and Discord-bot-list token ready"
while true; do
    read -p "Is this correct? [Yy/Nn]" yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) exit;;
        * ) echo "Please answer y or n";;
    esac
done

echo "Installing apt dependencies"
sudo apt install redis-server

echo "Setting correct owner and permissions for /opt/SpaceX-Launch-Bot"
sudo chown -R SLB:SLB /opt/SpaceX-Launch-Bot
sudo chmod -R u+rwX,go+rX,go-w /opt/SpaceX-Launch-Bot

echo "Setting up /var/log/SLB"
sudo mkdir /var/log/SLB
sudo chown SLB:SLB /var/log/SLB

echo "Install Python3 requirements through pip3"
sudo pip3 install -r requirements.txt

echo "This script will now open SLB.service for you to input your Discord and DLB tokens into"
echo "SLB will not work without you doing this"
read -p "Press enter to continue"
sudo cp -R -p services/systemd/. /etc/systemd/system/.
sudo nano /etc/systemd/system/SLB.service

echo "Copying redis config to /etc/redis"
sudo cp -R services/redis/. /etc/redis
echo "Restarting Redis"
sudo systemctl reload redis

echo "This script will now open config.json for you to fill out"
read -p "Press enter to continue"
sudo nano /opt/SpaceX-Launch-Bot/source/config/config.json

while true; do
    read -p "Start SLB service now? [Yy/Nn]" yn
    case $yn in
        [Yy]* ) sudo systemctl enable SLB; sudo systemctl start SLB; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer y or n";;
    esac
done
