# Web Server

A simple webserver for showing information about SpaceX-Launch-Bot. Written in Python+Flask using uWSGI to host, and using NGINX as a reverse proxy. Currently just parses the bots log file into HTML and then serves it over HTTP

Everywhere else (systemd config, NGINX config, etc.) this is refered to as `SLB-webServer`, but since this is already in the SpaceX-Launch-Bot directory, it is just referred to as `webServer` here

See [here](https://www.nginx.com/resources/glossary/reverse-proxy-server/) for why NGINX is used

This allows me to easily see what is happening with the bot without having to SSH into my server

It currently does not require authentication to view as nothing personal, private or important is logged

Read `../SETUP.md` to install this correctly
