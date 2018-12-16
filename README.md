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

A Discord bot for getting news and information about upcoming SpaceX launches. The bot also provides a notification service for updating you with the latest launch information, and reminders for launches that will be happening soon.

## Commands

Command|Description|Permissions needed
---|---|---
`!nextlaunch`|Send the latest launch information message to the current channel|None
`!addchannel`|Add the current channel to the notification service|Admin
`!removechannel`|Remove the current channel from the notification service|Admin
`!addping @role`|Add roles/users to be pinged when a "launching soon" message is sent. Can be formatted with multiple mentions in any order, like this: `!addping @role1 @user1 @role2`. Calling `!addping` multiple times will not stack the roles, it will just overwrite your previous settings|Admin
`!removeping`|Stop any roles/users on the server being pinged when a "launching soon" message is sent|Admin
`!info`|Show information about the bot|None
`!help`|List these commands|None

## Notification service

The `!addchannel` command allows admins to "subscribe" text channels to the bots notification service. This will send the subscribed channel different types of messages, which are explained below.

- A **launch information** message shows detailed information about the next upcoming launch. This message is sent every time the next upcoming launch has changed, e.g. if a launch date is changed or if a launch just happened so now the next upcoming launch is different. Currently the bot checks for changes every 15 minutes.

![LaunchInfo](images/screenshots/launchInfo.png)

- A **launching soon** message provides useful links to things such as the livestream and press kit. This message is only sent through the notification service and will be sent roughly 15 minutes (not exact due to technical reasons) before a launch actually happens.

![LaunchNotif](images/screenshots/launchNotif.png)

---

## Planned Updates / Improvments

- [x] Make this readme better (easier to read, understand, etc.)
- [ ] Allow more per-server settings (such as types of notifs, etc.)
- [ ] Improve `info` command (more info, better formatting)
- [ ] Add a voting command or some way of insetivising / integrating DBL voting
- [x] Restructure Redis
- [x] Generally clean up code
  - [x] Clean up `/modules`, seperate into more meaningful dirs
  - [x] Store settings, data, etc. in objects instead of dicts (where appropriate0)
  - [x] Clean up embed generation
    - [x] Make "launching soon" messages look a bit better
  - [x] Only refer to messages as "launch information" or "launching soon" messages
- [ ] "Allowing a mention as the prefix ("@MyBot help") or adding a way to find the bot's prefix with only a mention ("@MyBot" or "@MyBot, what's your prefix?") will help users who are new to your bot in getting started. (Make sure that whatever the message is, it's easily found. A great way to do this is by including it in your bot's presence.)"
- [x] Complete in-code TODOs
- [x] Add field in launch information embeds to show whether any stages are landing (and if so, where / on what)
