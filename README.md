# SpaceX-Launch-Bot

A Discord bot for gathering news and info about upcoming SpaceX launches

[**Add this bot to your server**](https://discordapp.com/oauth2/authorize?client_id=411618411169447950&scope=bot&permissions=248896)

# What does this bot do?

 - Allow users to see information about the closest launch by using a command
 - Allows users to "subscribe" channels to the bots launch notification service. This service will send a new message to the channel every time the next upcoming launch has changed (e.g. if a launch date is changed or if a launch just happened so now the next upcoming launch is different)

# Commands

Each command requires a prefix (the default is "!"), this can be changed by editing `PREFIX = "!"` in `main.py` to whatever you want

 - `!nextlaunch` - Show info about the next upcoming launch - any user can use this command
 - `!addchannel` - Add the current channel to the bots launch notification service - only admins can use this command
 - `!removechannel` - Remove the current channel to the bots launch notification service - only admins can use this command
 - `!info` - Information about the bot - any user can use this command
 - `!help` - List these commands - any user can use this command
 
 # Technical Info
 
 The API used it the [r/Space-X API](https://github.com/r-spacex/SpaceX-API)

# ToDo

 - Fix embed not sending when > 2000 chars (maybe split into multiple embeds?) (currently just sends link to reddit thread isntead of embed)
 - Show in notifications what has changed since the last message, e.g. if just the date has changed or if it is a new launch #
 - Send a notification when a launch is about to happen, maybe with a link to livestream / press kit
