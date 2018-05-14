# Config

`config.json` structure:

key | value type | value description
-|-|-
commandPrefix|String|The prefix needed to activate a command
apiCheckInterval|Int|The interval time, in minutes, between checking the SpaceX API for updates
launchNotificationDelta|Int|How far into the future to look for launches that are happening soon (in minutes). Should be at least apiCheckInterval * 2
dblIntegration|Bool|Whether or not to use the discordbots.org API
dblPostInterval|Int|The interval time, in minutes, between posting the bots server count to the discordbots.org API
