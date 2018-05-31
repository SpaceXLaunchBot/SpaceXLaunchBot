"""
Main server code
"""

from flask import Flask, render_template
from logParser import tailLog

app = Flask(__name__)

@app.route("/")
def showLog():
    logEntries = tailLog(20)
    return render_template("index.html", logEntries=logEntries)

if __name__ == "__main__":
    print("RUNNING IN DEBUG MODE")
    app.run(host="0.0.0.0", port=80, debug=True)
