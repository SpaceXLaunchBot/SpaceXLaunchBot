<h1 align="center" style="font-weight: bold">SpaceX Launch Bot</h1>

<p align="center">
    <a href="https://discordbots.org/bot/411618411169447950" >
        <img src="https://discordbots.org/api/widget/status/411618411169447950.svg?noavatar=true" alt="SpaceX-Launch-Bot" />
    </a>
    <a href="https://discordbots.org/bot/411618411169447950" >
        <img src="https://discordbots.org/api/widget/servers/411618411169447950.svg?noavatar=true" alt="SpaceX-Launch-Bot" />
    </a>
    <a href="https://discordbots.org/bot/411618411169447950" >
        <img src="https://discordbots.org/api/widget/upvotes/411618411169447950.svg?noavatar=true" alt="SpaceX-Launch-Bot" />
    </a>
    <br/>
    <a href="https://discordapp.com/oauth2/authorize?client_id=411618411169447950&scope=bot&permissions=19456" alt="Discord Invite">
        <img src="https://img.shields.io/badge/Discord-Bot%20Invite-blue.svg?style=flat&colorA=35383d"/>
    </a>
    <a href="https://ko-fi.com/M4M18XB1">
        <img src="https://img.shields.io/badge/Ko--fi-Donate-orange.svg?style=flat&colorA=35383d"/>
    </a>
    <br/>
    <a href="https://discordbots.org/bot/411618411169447950" >
        <img src="https://discordbots.org/api/widget/owner/411618411169447950.svg?noavatar=truee" alt="SpaceX-Launch-Bot" />
    </a>
</p>

A Discord bot for getting news, information, and notifications about upcoming SpaceX launches. The notification service updates you with the latest launch information, and reminders for launches that will be happening soon.

## Commands

Command|Description|Permissions needed
---|---|---
`!nextlaunch`|Send the latest launch information message to the current channel|None
`!addchannel`|Add the current channel to the notification service|Admin
`!removechannel`|Remove the current channel from the notification service|Admin
`!setmentions @mention`|Set roles/users to be mentioned when a "launching soon" message is sent. Can be formatted with multiple mentions in any order, like this: `!setmentions @role1 @user1 @role2`. Calling `!setmentions` multiple times will not stack the roles, it will just overwrite your previous mentions|Admin
`!removementions`|Remove all mentions set for the current guild|Admin
`!getmentions`|Get mentions set for the current guild|Admin
`!info`|Show information about the bot|None
`!help`|List these commands|None

## Notifications

The `!addchannel` command allows admins to "subscribe" text channels to the bots notification service. This will send the subscribed channel different types of messages, which are explained below.

- A **launch information message** shows detailed information about the next upcoming launch. This message is sent every time the next upcoming launch has changed, e.g. if a launch date is changed or if a launch just happened so now the next upcoming launch is different. Currently the bot checks for changes every 15 minutes.

![launchInfo](images/screenshots/launchInfo.png)

- A **launching soon message** provides useful links to things such as the livestream and press kit. This message is only sent through the notification service and will be sent roughly 15 minutes (not exact due to technical reasons) before a launch actually happens.

![launchSoon](images/screenshots/launchSoon.png)

---

## Planned Updates / Improvments

- [ ] Finish new background tasks
- [ ] Improve `info` command (more info, better formatting)
