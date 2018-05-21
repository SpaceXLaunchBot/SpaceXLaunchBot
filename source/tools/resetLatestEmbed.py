"""
Reset the latest launch embed in data.pkl, so that an update is sent out
"""

import sys
sys.path.append("..")

from general import warning

from modules import fs
from modules.errors import nextLaunchErrorEmbed

warning()  # Ask/show user important stuff

# Lock not needed since bot is not currently running
fs.localData["latestLaunchInfoEmbedDict"] = nextLaunchErrorEmbed.to_dict()
fs.saveLocalDataSync()
print("latestLaunchInfoEmbedDict saved to localData")
