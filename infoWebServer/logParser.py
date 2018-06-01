from time import time
from os import path
import re

logFilePath = path.join(path.dirname(path.abspath(__file__)), "..", "logs", "bot.log")
# Regex for yyyy:mm:dd hh:mm:ss,ms
dateTimeFormat = re.compile("^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}),(\d{3})")
logFileSplitter = " : "

class logEntry(object):
    def __init__(self, time, level, route, message):
        self.time    : str = time
        self.level   : str = level
        self.route   : str = route
        self.message : str = message

def tailLog(n):
    """
    Get the last $n lines of the log and parse into
    logEntry objects
    """
    logObjects = []
    entriesRead = 0  # The amount of individual log entries read

    try:
        with open(logFilePath, "r") as logFile:
            # Only get last $n lines
            linesToRead = logFile.readlines()[-n:]
    except FileNotFoundError:
        return logEntry("", "CRITICAL", "", "Log file does not exist")

    for line in linesToRead:
        line = line.strip()

        # If new log entry
        if dateTimeFormat.match(line):
            if entriesRead == n:
                break
            
            # Get parts of log entry and create the logEntry object
            lineInfo = line.split(logFileSplitter)
            logObjects.append(logEntry(*lineInfo))
            entriesRead += 1
        
        # Else this line is part of the previous log entry
        else:
            if len(logObjects) == 0:
                # We have started reading the file at a multi-line message
                continue
            logObjects[-1].message += " " + line

    return logObjects
