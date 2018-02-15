import pickle
import sys

botInfo = """
This bot displays information about the latest upcoming SpaceX launches from the r/Space-X API

*Website: https://thatguywiththatname.github.io/SpaceX-Launch-Bot*
*Github: https://github.com/thatguywiththatname/SpaceX-Launch-Bot*
"""

helpText = """
Command prefix: {prefix}

Commands:
 • `!nextlaunch` - Show info about the next upcoming launch - any user can use this command
 • `!info` - Information about the bot - any user can use this command
 • `!help` - List these commands - any user can use this command
"""

def err(message):
    print("\nERROR:\n" + message)
    sys.exit(-1)

def saveDict(dictObj):
    with open("resources/dict.pkl", "wb") as f:
        pickle.dump(dictObj, f, pickle.HIGHEST_PROTOCOL)

def loadDict():
    try:
        with open("resources/dict.pkl", "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        # No .pkl, create default dict, save to file & return
        temp = {"subscribedChannels":[], "nextLaunchJSON":{}}
        saveDict(temp)
        return temp
