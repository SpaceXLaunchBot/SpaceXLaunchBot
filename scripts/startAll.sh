# Enable and start all of the services that the SLBsetup process installs 

sudo systemctl daemon-reload
sudo systemctl enable redis
sudo systemctl start redis
sudo systemctl enable SLB
sudo systemctl start SLB
sudo systemctl enable SLB-webServer
sudo systemctl start SLB-webServer
sudo systemctl enable netdata
sudo systemctl start netdata
sudo systemctl restart nginx
