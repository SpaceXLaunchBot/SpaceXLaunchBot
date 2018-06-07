<p align="center">
<img width="400" src="https://discordbots.org/api/widget/411618411169447950.svg" href='https://discordbots.org/bot/411618411169447950'>
</p>

<p align="center">
A Discord bot for providing news and information about upcoming SpaceX launches
</p>

<p align="center">
The bot also provides a notification service for updating you with the latest launch information, and reminders for launches that will be happening soon
</p>

<p align="center"><b><a href="https://discordapp.com/oauth2/authorize?client_id=411618411169447950&scope=bot&permissions=248896">Add this bot to your server</a> | <a href="https://discordbots.org/bot/411618411169447950">View on discordbots.org</a></b></p>

# What does this bot do?

This bot mainly sends 2 types of messages:

- A launch information message shows detailed information about the next upcoming launch. This is sent through the notification service as well as when the `!nextlaunch` command is used

- A launch notification message that provides useful links to things such as the livestream and press kit. This message is only sent through the notification service (more details below)

## Commands

Command|Description|Permissions needed
---|---|---
`!nextlaunch`|Send the latest launch information message to the current channel|None
`!addchannel`|Add the current channel to the launch notification service|Admin
`!removechannel`|Remove the current channel from the launch notification service|Admin
`!info`|Show information about the bot|None
`!help`|List these commands|None

## Launch notification service

The `!addchannel` command allows admins to "subscribe" text channels to the bots notification service

This means the bot will send a new launch information message to the subscribed channel every time the next upcoming launch has changed, e.g. if a launch date is changed or if a launch just happened so now the next upcoming launch is different

A launch notification message will be sent around 15 minutes (not exact, due to technical reasons) before a launch actually happens

## Message examples

Launch information:

![LaunchInfo](screenshots/launchInfo.png)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fr-spacex%2FSpaceX-Launch-Bot.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fr-spacex%2FSpaceX-Launch-Bot?ref=badge_shield)

Launch notification:

![LaunchNotif](screenshots/launchNotif.png)


## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fr-spacex%2FSpaceX-Launch-Bot.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fr-spacex%2FSpaceX-Launch-Bot?ref=badge_large)