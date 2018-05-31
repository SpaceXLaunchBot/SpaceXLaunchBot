"""
Start the server
"""

from flask import Flask, render_template
from logParser import tailLog
import ipgetter
import logging

app = Flask(__name__)

@app.route("/")
def showLog():
    logEntries = tailLog(20)
    return render_template("index.html", logEntries=logEntries)

if __name__ == "__main__":
    # Yep, logging this to a file as well
    logging.basicConfig(filename="../logServer.log", level=logging.INFO)
    app.run(host="0.0.0.0", port=80)
