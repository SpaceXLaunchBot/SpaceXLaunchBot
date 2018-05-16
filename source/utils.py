"""
General utility variables & functions, for example:
 + Time conversions
 + Variable validation
"""

from datetime import datetime
from os import environ

from errors import fatalError

async def isInt(possiblyInteger):
    try:
        int(possiblyInteger)
        return True
    except ValueError:
        return False

async def UTCFromTimestamp(timestamp):
    dateIsInt = await isInt(timestamp)
    if dateIsInt:
        formattedDate = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        return "{} UTC".format(formattedDate)
    return "To Be Announced"

def loadEnvVar(varName):
    """
    Returns the environment variable $varName, or exits program with error msg
    """
    try:
        return environ[varName]
    except KeyError:
        fatalError("Environment Variable \"{}\" cannot be found".format(varName))
