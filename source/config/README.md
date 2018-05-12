# Config

`config.json` structure:

key | value type | value description
-|-|-
commandPrefix|String|The prefix needed to activate a command
apiCheckInterval|Int|The interval time, in minutes, between checking the API for updates
launchNotificationDelta|Int|How far into the future to look for launches that are happening soon (in minutes). Should be at least apiCheckInterval * 2
dblIntegration|Bool|Whether or not to load & use the discordbots.org API
