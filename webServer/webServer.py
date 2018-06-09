"""
Main server code
"""

from flask import Flask, render_template
from logParser import tailLog
import requests
import pickle
import redis
import json

# Get bot info from Discord bot list API (num servers, etc.)
botInfoURL = "https://discordbots.org/api/bots/411618411169447950"

# TODO: Subclass StrictRedis and make the db requests safe
redisConn = redis.StrictRedis(unix_socket_path="/tmp/redis.sock", db=0)

app = Flask(__name__)

@app.route("/")
def showLandingPage():

    subbedChannelCount = len(pickle.loads(redisConn.get("subscribedChannels")))

    # TODO: Some form of caching for this request
    resp = requests.get(botInfoURL)
    botData = json.loads(resp.text)

    # Using the Discord image CDN, get avatar using info from the DBL data
    botAvatarURL = f"https://images.discordapp.net/avatars/{botData['clientid']}/{botData['avatar']}.png?size=128"

    return render_template(
        "index.html",
        numServers = botData["server_count"],
        subbedChannelCount = subbedChannelCount,
        botAvatarURL = botAvatarURL
    )

@app.route("/log")
def showLog():
    logEntries = tailLog(15)
    return render_template("log.html", logEntries=logEntries)

if __name__ == "__main__":
    print("RUNNING IN DEBUG MODE")
    app.run(host="127.0.0.1", port=8080, debug=True)
