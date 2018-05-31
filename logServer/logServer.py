"""
Main server code
"""

from flask import Flask, render_template
from logParser import tailLog

app = Flask(__name__)

@app.route("/")
def showLog():
    logEntries = tailLog(15)
    return render_template("index.html", logEntries=logEntries)

if __name__ == "__main__":
    print("RUNNING IN DEBUG MODE")
    app.run(host="127.0.0.1", port=8080, debug=True)
