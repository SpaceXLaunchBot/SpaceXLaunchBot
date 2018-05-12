"""
Reset launchNotifSent in data.pkl
"""

import sys
sys.path.append("..")

from general import warning
import utils

warning()  # Ask/show user important stuff
localData = utils.loadLocalData()
localData["launchNotifSent"] = False

utils.saveLocalDataSync(localData)
print("launchNotifSent set to False")
