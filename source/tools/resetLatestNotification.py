"""
Reset launchNotifSent in data.pkl
"""

import sys
sys.path.append("..")

from general import warning

from modules import fs

warning()  # Ask/show user important stuff

fs.localData["launchNotifSent"] = False
fs.saveLocalDataSync()
print("launchNotifSent set to False")
