"""
Main server code
"""

from flask import Flask, render_template
from datetime import timedelta
import requests
import json

from modules.redisClient import redisClient
from modules.logParser import tailLog
from modules.cache import cache

# Get bot info from Discord bot list API (num servers, etc.)
botInfoURL = "https://discordbots.org/api/bots/411618411169447950"
def getDBLData():
    resp = requests.get(botInfoURL)
    return json.loads(resp.text)

redisConn = redisClient(unix_socket_path="/tmp/redis.sock", db=0)
botDataCache = cache(getDBLData, timedelta(hours=1))
app = Flask(__name__)

@app.route("/")
def showLandingPage():

    subbedChannels = redisConn.safeGet("subscribedChannels", True)
    if subbedChannels != 0:
        subbedChannelCount = len(subbedChannels)
    else:
        subbedChannelCount = "(unknown)"

    botData = botDataCache.get()

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
