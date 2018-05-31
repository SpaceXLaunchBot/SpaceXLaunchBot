# Config

`config.json` structure:

key | value type | value description
-|-|-
commandPrefix|String|The prefix needed to activate a command
apiCheckInterval|Int|The interval time, in minutes, between checking the SpaceX API for updates
launchNotificationDelta|Int|How far into the future to look for launches that are happening soon (in minutes). Should be at least apiCheckInterval * 2
reaperInterval|Int|Every $reaperInterval minutes, check for non-existant (dead) channels in subscribedChannels and remove them - Essentially garbage collection for the channel list
logFormat|String|The format for the log
