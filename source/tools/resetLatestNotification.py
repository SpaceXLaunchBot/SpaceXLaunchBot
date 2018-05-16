"""
Reset launchNotifSent in data.pkl
"""

import sys
sys.path.append("..")

from general import warning
import fs

warning()  # Ask/show user important stuff
localData = fs.loadLocalData()
localData["launchNotifSent"] = False

fs.saveLocalDataSync(localData)
print("launchNotifSent set to False")
