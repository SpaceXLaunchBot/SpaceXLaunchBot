# Web Server

A simple webserver for showing information about SpaceX-Launch-Bot. Written in Python+Flask using uWSGI to host, and using NGINX as a reverse proxy. Currently just parses the bots log file into HTML and then serves it over HTTP

Everywhere else (systemd config, NGINX config, etc.) this is refered to as `SLB-webServer`, but since this is already in the SpaceX-Launch-Bot directory, it is just referred to as `webServer` here

See [here](https://www.nginx.com/resources/glossary/reverse-proxy-server/) for why NGINX is used

## Pages

(all pages are currently `HTTP`)

URL|Description
-|-
`spacex-launch-bot.gq`|A basic landing page for people to see info & the invite for SLB
`status.spacex-launch-bot.gq`|A basic page to show various metrics and statuses from the server
`m.status.spacex-launch-bot.gq`|The same as `status` but for mobile (WIP)