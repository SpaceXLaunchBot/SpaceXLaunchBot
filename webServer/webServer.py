"""
Main web server
"""

from flask import Flask, render_template, jsonify, request
from imtfc import imtfc_cache
import requests
import json

from modules.redisClient import redisClient
from modules.logParser import tailLog

# Use the Discord bot list API for num guilds, avatar URL, etc.
botInfoURL = "https://discordbots.org/api/bots/411618411169447950"

# Setup time-based caching for the function so we don't spam the API
@imtfc_cache(hours=1)
def getDBLData():
    resp = requests.get(botInfoURL)
    return json.loads(resp.text)

redisConn = redisClient(unix_socket_path="/tmp/redis.sock", db=0)
app = Flask(__name__)

@app.route("/")
def showLandingPage():

    subbedChannels = redisConn.safeGet("subscribedChannels", True)
    if subbedChannels != 0:
        subbedChannelCount = len(subbedChannels)
    else:
        subbedChannelCount = "(unknown)"

    botData = getDBLData()

    # Using the Discord image CDN, get avatar using info from the DBL data
    botAvatarURL = f"https://images.discordapp.net/avatars/{botData['clientid']}/{botData['avatar']}.png?size=128"

    return render_template(
        "index.html",
        numGuilds = botData["server_count"],
        subbedChannelCount = subbedChannelCount,
        botAvatarURL = botAvatarURL
    )

@app.route("/api/log")
def showLog():
    """
    Serves the latest $count entries in the SLB log
    """
    n = request.args.get("count", default=30, type=int)
    logEntries = tailLog(n)
    return jsonify(logEntries)
