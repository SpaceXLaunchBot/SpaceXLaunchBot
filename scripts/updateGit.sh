# Pull latest updates from git repo
# For some reason it doesen't like just `git pull`
# sudo because file permissions
# chown because "sudo git" changes owner
sudo git fetch --all
sudo git reset --hard origin/master
sudo chown -R SLB /opt/SpaceX-Launch-Bot