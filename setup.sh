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
 - The latest version of the "redis-server" package from apt
 - The latest version of pip for python3 using pypa's get-pip.py
Make sure:
 - Python 3.6+ exists under the "python3" command
 - The SLB files exist in /opt/SpaceXLaunchBot
 - You have a Discord bot token
 - You have a Discord Bot List token

EndOfMsg

askyn "Is this correct?" || exit

cd /opt/SpaceXLaunchBot

echo "Installing apt dependencies"
sudo apt install python3-venv redis-server -y

echo "Installing pip"
# pip is not actually required to make the venv, but installing this means that:
# - There is no confusion between system-wide pip and the pip that's copied to the venv
# - The default packages (setuptools, wheel) are installed correctly
curl https://bootstrap.pypa.io/get-pip.py | sudo python3

echo "Setting up slb-venv"
sudo python3 -m venv slb-venv
echo "Installing Py3 requirements inside slb-venv"
sudo slb-venv/bin/pip3 install -r requirements.txt

echo "Setting correct owner and permissions for /opt/SpaceXLaunchBot"
sudo adduser --system --group --no-create-home spacexlaunchbot
sudo chown -R spacexlaunchbot:spacexlaunchbot /opt/SpaceXLaunchBot
sudo chmod -R u+rwX,go+rX,go-w /opt/SpaceXLaunchBot

echo "Setting up /var/log/spacexlaunchbot"
sudo mkdir /var/log/spacexlaunchbot
sudo chown spacexlaunchbot:spacexlaunchbot /var/log/spacexlaunchbot

echo "Copying over systemd file(s)"
sudo cp -R -p services/systemd/. /etc/systemd/system

echo "Copying redis config to /etc/redis"
# Redis looks for a config file here by default
sudo cp -R services/redis/. /etc/redis
echo "Restarting Redis"
sudo systemctl restart redis

if askyn "Edit spacexlaunchbot.service now? This will have to be done before running it";
then sudo nano /etc/systemd/system/spacexlaunchbot.service; fi

cat << EndOfMsg

Setup finished
--------------
If you have a dump.rdb, stop redis, move it to /var/lib/redis and then start it again
To start SLB enable and start it using systemd

EndOfMsg

# To get a copy of dump.rdb:
# $ sudo cp /var/lib/redis/dump.rdb ~/
# $ sudo chwon USER dump.rdb
# --> Download from server
