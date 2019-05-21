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

# https://stackoverflow.com/a/34143401/6396652
exists() {
  command -v "$1" >/dev/null 2>&1
}

cat << EndOfMsg

SpaceXLaunchBot Setup
---------------------

This script will install these dependencies:
- The latest version of these packages from apt:
 - python3-venv
 - redis-server
- If pip3 is not installed, the latest version of pip for Py3 using pypa's get-pip.py

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

# pip is not actually required to make the venv, but installing this means that:
# - There is no confusion between system-wide pip and the pip that's copied to the venv
# - The default packages (setuptools, wheel) are installed correctly
if ! exists pip3; then
    echo "Installing pip"
    curl https://bootstrap.pypa.io/get-pip.py | sudo python3
fi

echo "Setting up slb-venv"
sudo python3 -m venv slb-venv
echo "Installing Py3 requirements inside slb-venv"
sudo slb-venv/bin/pip3 install -r requirements.txt

echo "Setting correct owner and permissions for /opt/SpaceXLaunchBot"
sudo adduser --system --group --no-create-home spacexlaunchbot
sudo chown -R spacexlaunchbot:spacexlaunchbot /opt/SpaceXLaunchBot
# Permissions Explanation
# Capital X --> https://www.g-loaded.eu/2005/11/08/the-use-of-the-uppercase-x-in-chmod/
# Give owner of the file (spacexlaunchbot) the ability to r, w, and X all files
# Allow everyone else to r and X, don't allow anyone else to w
sudo chmod -R u+rwX,go+rX,go-w /opt/SpaceXLaunchBot

echo "Setting up /var/log/spacexlaunchbot"
sudo mkdir /var/log/spacexlaunchbot
sudo chown spacexlaunchbot:spacexlaunchbot /var/log/spacexlaunchbot

echo "Copying over systemd file(s)"
sudo cp -R -p services/systemd/. /etc/systemd/system

echo "Copying redis config to /etc/redis"
# The apt installed version of redis-server looks for a config file here by default
sudo cp -R services/redis/. /etc/redis
echo "Restarting Redis"
sudo systemctl restart redis

if askyn "Edit spacexlaunchbot.service now? This will have to be done before running it";
then sudo nano /etc/systemd/system/spacexlaunchbot.service; fi

cat << EndOfMsg

Setup Finished
--------------
If you have a dump.rdb, stop redis, move it to /var/lib/redis and then start it again
To start SLB enable and start it using systemctl

EndOfMsg

# To get a copy of dump.rdb:
# $ sudo cp /var/lib/redis/dump.rdb ~/
# $ sudo chwon USER dump.rdb
# --> Download from server
