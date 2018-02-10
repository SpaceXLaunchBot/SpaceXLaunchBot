# SpaceX-Launch-Bot

A Discord bot for gathering news and info about upcoming SpaceX launches

[**Add this bot to your server**](https://discordapp.com/oauth2/authorize?client_id=411618411169447950&scope=bot&permissions=248896)

# What does this bot do?

This bot essentially performs 2 functions:

 - Provide a "subscribed" channel with up to date information about upcoming SpaceX launches
 - Allow users to see information about the closest launch by using a command

# Commands

The command prefix can be changed by editing `PREFIX = "!"` in `main.py` to whatever you want

 - `!addchannel` - Subscribe the channel to the bots notification service - admins only
 - `!nextlaunch` - Show info about the next upcoming launch - any user can use this command
 - `!info` - Information about the bot - any user can use this command
 - `!help` - List these commands - any user can use this command
 
 # Technical Info
 
 The API used it the [r/Space-X API](https://github.com/r-spacex/SpaceX-API)
 
