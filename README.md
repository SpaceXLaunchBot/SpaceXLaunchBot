<p align="center">
<img width="400" src="https://discordbots.org/api/widget/411618411169447950.svg" href='https://discordbots.org/bot/411618411169447950'>
</p>

<p align="center">
A Discord bot for providing news and information about upcoming SpaceX launches
</p>
<p align="center">
Also provides a notification service for launch information and reminders for launches happening soon
</p>

<p align="center"><b><a href="https://discordapp.com/oauth2/authorize?client_id=411618411169447950&scope=bot&permissions=248896">Add this bot to your server</a> | <a href="https://discordbots.org/bot/411618411169447950">View on discordbots.org</a></b></p>

# What does this bot do?

Command|Description|Permissions needed
---|---|---
`!nextlaunch`|Show info about the next upcoming launch|None
`!addchannel`|Add the current channel to the bots launch notification service|Admin
`!removechannel`|Remove the current channel to the bots launch notification service|Admin
`!info`|Information about the bot|None
`!help`|List these commands|None

## Launch notification service

The `!addchannel` comamnd allows admins to "subscribe" channels to the bots launch notification service. This service will send a new message to the channel every time the next upcoming launch has changed (e.g. if a launch date is changed or if a launch just happened so now the next upcoming launch is different). A notification will also be sent around 15 minutes (not exact, due to technical reasons) before a launch, containing useful links such as the livestream and the press kit

## Message examples

Launch Info:

![LaunchInfo](screenshots/launchInfo.png)

Launch Notification:

![LaunchNotif](screenshots/launchNotif.png)
