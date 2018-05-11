"""
Reset the latest launch embed in data.pkl, so that an update is sent out
"""

import sys
sys.path.append("..")

from general import warning
import utils

warning()  # Ask/show user important stuff
localData = utils.loadDict()
localData["latestLaunchInfoEmbed"] = utils.nextLaunchErrorEmbed

utils.saveDictSync(localData)
print("latestLaunchInfoEmbed saved to localData")
