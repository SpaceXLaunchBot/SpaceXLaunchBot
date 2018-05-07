"""
Reset the latest launch embed in dict.pkl, so that an update is sent
out within the next 30 mins (the rate at which the bot checks for new
launch info)
"""

import sys
sys.path.append("..")

from general import warning
import utils

warning()  # Ask/show user important stuff

launchNotifDict = utils.loadDict()

launchNotifDict["nextLaunchEmbed"] = utils.nextLaunchErrorEmbed
utils.saveDict(launchNotifDict)

print("nextLaunchErrorEmbed saved to launchNotifDict")
