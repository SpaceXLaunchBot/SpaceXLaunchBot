"""
General utility variables & functions, for example:
 + Time conversions
 + Variable validation
"""

from datetime import datetime
from os import environ

from modules.errors import fatalError

async def isInt(possiblyInteger):
    try:
        int(possiblyInteger)
        return True
    except ValueError:
        return False

# TODO: Rename this to be more specific to launch-time timestamps
async def UTCFromTimestamp(timestamp):
    dateIsInt = await isInt(timestamp)
    if dateIsInt:
        formattedDate = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        return f"{formattedDate} UTC"
    return "To Be Announced"

def loadEnvVar(varName):
    """
    Returns the environment variable $varName, or exits program with error msg
    """
    try:
        return environ[varName]
    except KeyError:
        fatalError(f"Environment Variable \"{varName}\" cannot be found")
