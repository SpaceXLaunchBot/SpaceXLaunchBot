"""
Temp file - convert old data.pkl structure to newer, better structure
"""

import sys
sys.path.append("..")

from general import warning

from modules import fs  # Loaded from file on import

warning()  # Ask/show user important stuff

fs.localData["latestLaunchInfoEmbedDict"] = fs.localData["latestLaunchInfoEmbed"].to_dict()
del fs.localData["latestLaunchInfoEmbed"]

fs.saveLocalDataSync()

print("Done")
