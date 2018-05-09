"""
Temporary - convert old dict.pkl to new data.pkl
"""
import sys
sys.path.append("..")

from general import warning
import pickle
import utils

warning()  # Ask/show user important stuff

with open("../resources/dict.pkl", "rb") as f:
    oldLocalData = pickle.load(f)

localData = {}
localData["subscribedChannels"]    = oldLocalData["subscribedChannels"]
localData["latestLaunchInfoEmbed"] = oldLocalData["nextLaunchEmbed"]
localData["launchNotifSent"]       = False

utils.saveDictSync(localData)
print("New info saved to data.pkl")
