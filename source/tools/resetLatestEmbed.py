"""
Reset the latest launch embed in data.pkl, so that an update is sent out
"""

import sys
sys.path.append("..")

from errors import nextLaunchErrorEmbed
from general import warning
import fs

warning()  # Ask/show user important stuff
localData = fs.loadLocalData()
localData["latestLaunchInfoEmbed"] = nextLaunchErrorEmbed

fs.saveLocalDataSync(localData)
print("latestLaunchInfoEmbed saved to localData")
