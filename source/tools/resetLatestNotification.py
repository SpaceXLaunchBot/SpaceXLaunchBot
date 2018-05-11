"""
Reset launchNotifSent in data.pkl
"""

import sys
sys.path.append("..")

from general import warning
import utils

warning()  # Ask/show user important stuff
localData = utils.loadDict()
localData["launchNotifSent"] = False

utils.saveDictSync(localData)
print("launchNotifSent set to False")
