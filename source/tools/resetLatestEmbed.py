"""
Reset the latest launch embed in data.pkl, so that an update is sent out
"""

import sys
sys.path.append("..")

from errors import nextLaunchErrorEmbed
from general import warning
import fs

warning()  # Ask/show user important stuff

# Lock not needed since bot is not currently running
fs.localData["latestLaunchInfoEmbed"] = nextLaunchErrorEmbed
fs.saveLocalDataSync()
print("latestLaunchInfoEmbed saved to localData")
