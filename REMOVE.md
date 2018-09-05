# Uninstall / remove components installed in SETUP.md

## Web server realted components

This is for when you have another use for the web serving capabilities of the
server and don't want SLB-webServer, netdata, etc using up an ip/port/domain name

### Remove just slb-webServer stuff

```bash
systemctl disable SLB-webServer
systemctl stop SLB-webServer

rm /lib/systemd/system/SLB-webServer.service

systemctl daemon-reload
systemctl reset-failed

rm /etc/nginx/sites-enabled/SLB-webServer
rm /etc/nginx/sites-available/SLB-webServer

rm /etc/nginx/sites-enabled/SLB-webServer-status
rm /etc/nginx/sites-available/SLB-webServer-status
```

### Remove nginx and netdata

Easier to switch to su to execute these:

```bash
systemctl disable netdata
systemctl stop netdata

killall netdata
# Not tested - these might be used by somethig else
apt-get remove zlib1g-dev autoconf autogen automake pkg-config -y

rm -Rf /usr/sbin/netdata
rm -Rf /etc/netdata
rm -Rf /usr/share/netdata
rm -Rf /usr/libexec/netdata
rm -Rf /var/cache/netdata
rm -Rf /var/log/netdata
rm -Rf /opt/netdata

userdel netdata

rm /etc/nginx/sites-enabled/netdata-webServer
rm /etc/nginx/sites-available/netdata-webServer

systemctl disable nginx
systemctl stop nginx

sudo apt remove nginx -y

systemctl daemon-reload
systemctl reset-failed
```
