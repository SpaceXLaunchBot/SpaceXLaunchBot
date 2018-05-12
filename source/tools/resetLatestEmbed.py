"""
Reset the latest launch embed in data.pkl, so that an update is sent out
"""

import sys
sys.path.append("..")

from general import warning
import utils

warning()  # Ask/show user important stuff
localData = utils.loadLocalData()
localData["latestLaunchInfoEmbed"] = utils.nextLaunchErrorEmbed

utils.saveLocalDataSync(localData)
print("latestLaunchInfoEmbed saved to localData")
