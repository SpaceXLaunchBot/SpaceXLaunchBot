"""
Safely serve the log server app
https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-16-04

To run:
$ uwsgi --ini infoWebServer.ini
"""

from infoWebServer import app

if __name__ == "__main__":
    app.run()
