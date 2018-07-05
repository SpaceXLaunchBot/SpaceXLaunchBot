"""
Safely serve the log server app
https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-16-04

To run for prod:
$ uwsgi --ini webServer.ini

For debugging / local development:
$ python3 startServer.py
"""

from webServer import app

if __name__ == "__main__":
    print(f"{'*'*10} RUNNING IN DEBUG MODE {'*'*10}")
    app.run(debug=True)
