from time import time
from os import path
import re

logFilePath = path.join(path.dirname(path.abspath(__file__)), "..", "..", "logs", "bot.log")
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

    """
    Since we are reading the log in reverse order, logs that have multi-line
    entries will need to be built up over the lines they span, then added into
    a logEntry object when the start of that log entry is found. currentMessage
    will hold all of the lines in that multi-line entry until the start of the
    entry is found, it is then join()ed into the logEntry obj and reset to []
    """
    currentMessage = []
    entriesRead = 0  # The amount of individual log entries read

    try:
        with open(logFilePath, "r") as logFile:
            linesToRead = logFile.readlines()
    except FileNotFoundError:
        return [logEntry("", "CRITICAL", "", "Log file does not exist")]

    for line in reversed(linesToRead):
        # Get parts of log entry
        line = line.strip()

        # If new log entry
        if dateTimeFormat.match(line):
            if entriesRead == n:
                break
            
            lineInfo = line.split(logFileSplitter)
            """
            If there were multiple lines to this log message then concat them
            all now and append them to the current message section of the line
            """
            lineInfo[-1] += " " + " ".join(currentMessage)
            currentMessage = []

            logObjects.append(logEntry(*lineInfo))
            entriesRead += 1
        
        # Else this line is part of the next upcoming log entry
        else:
            """
            Insert this line of text into the currentMessage list. Inserted at
            the start so multi-line entries aren't displayed backwards, as we
            are reading the message(s) in reverse order
            """
            currentMessage.insert(0, line)

    """
    We read in reverse order to get the last $n entries, so now reverse back
    into chronological order
    """
    return reversed(logObjects)
