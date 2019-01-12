# Config

`config.json` structure:

key | value type | value description
-|-|-
ownerID|String|The Discord ID of the person running the bot
commandPrefix|String|The prefix needed to activate a command
apiCheckInterval|Int|The interval time, in minutes, between checking the SpaceX API for updates
launchSoonDelta|Int|How far into the future to look for launches that are happening soon (in minutes). Should be at least apiCheckInterval * 2 otherwise launching soon notifications may be missed
logFilePath|String|The path to save the log file to
logFormat|String|The format for the log
colours|Object containing Arrays|The colours used for different cases:<br>errorRed: used in error related embeds<br>falconRed: used in rocket info / launch embeds
game|String|The "game" the bot will play