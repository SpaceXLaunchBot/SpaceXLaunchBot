"""
Deconstructs data.pkl into a JSON file, allowing for easy debugging
"""

import sys
from json import dump
sys.path.append("..")

from general import warning

from modules import fs  # Loaded from file on import

warning()  # Ask/show user important stuff

# data.json is in gitignore
with open("data.json", "w") as outFile:
    dump(fs.localData, outFile)

print("data.pkl dumped to data.json")
