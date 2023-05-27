<h1 align="center" style="font-weight: bold">SpaceX Launch Bot</h1>

<p align="center">
    <a href="https://top.gg/bot/411618411169447950" >
        <img src="https://top.gg/api/widget/status/411618411169447950.svg?noavatar=true" alt="SpaceXLaunchBot status" />
    </a>
    <a href="https://top.gg/bot/411618411169447950" >
        <img src="https://top.gg/api/widget/servers/411618411169447950.svg?noavatar=true" alt="SpaceXLaunchBot server count" />
    </a>
    <a href="https://top.gg/user/3204220773157502976" >
        <img src="https://top.gg/api/widget/owner/411618411169447950.svg?noavatar=true" alt="SpaceXLaunchBot owner id" />
    </a>
    <br/>
    <a href="https://discord.com/oauth2/authorize?client_id=411618411169447950&scope=bot&permissions=2147633152">
        <img src="https://img.shields.io/badge/Discord-Bot%20Invite-blue.svg?style=flat&colorA=35383d" alt="Discord Invite"/>
    </a>
    <a href="https://discord.gg/j6vbHkYSES">
        <img src="https://img.shields.io/badge/Discord-Support%20Server%20Invite-blue.svg?style=flat&colorA=35383d" alt="Discord Support Server Invite"/>
    </a>
    <br/>
    <a href="https://github.com/r-spacex/SpaceXLaunchBot/actions">
        <img src="https://github.com/r-spacex/SpaceXLaunchBot/workflows/CI/badge.svg" alt="Github CI Build Status"/>
    </a>
    <a href="https://github.com/psf/black">
        <img src="https://img.shields.io/badge/Code%20Style-Black-000000.svg?colorA=35383d" alt="Black code formatter"/>
    </a>
</p>

A Discord bot for getting news, information, and notifications about upcoming SpaceX launches. Get update notifications with the latest launch information and reminders for launches that will be happening soon.

See the [official SpaceXLaunchBot website](https://spacexlaunchbot.dev/)!

## Commands

Command|Description|Permissions needed
---|---|---
`nextlaunch`|Send the latest launch schedule message to the current channel|None
`launch [launch number]`|Send the launch schedule message for the given launch number to the current channel|None
`add [type] [mentions]`|Add the current channel to the notification service with the given notification type (`all`, `schedule`, or `launch`). If you chose `all` or `launch`, the second part can be a list of roles / channels / users to ping when a launch notification is sent|Admin
`remove`|Remove the current channel from the notification service|Admin
`info`|Send information about the bot to the current channel|None
`help`|List these commands|None

## Notifications

The `add` command allows admins to subscribe text channels to the bots notification service. This will send the subscribed channel different types of messages:

- A **schedule** notification shows detailed information about the next upcoming launch. This message is sent every time the next upcoming launch has changed, e.g. if a launch date is changed or if a launch just happened so now the next upcoming launch is different. Currently changes are checked for every 60 seconds.

![launch_info](images/screenshots/launch_info.png)

- A **launch** notification provides useful links to things such as the livestream and press kit. This message is only sent through the notification service and will be sent 30 minutes before a launch. You can choose to have a list of mentions sent to alert users to this notification.

![launch_soon](images/screenshots/launch_soon.png)

If you want to receive both types of notification you can use **all**.

Currently there is no way to update the type and/or mentions you have set for a channel. If you need to change these just call `remove` and then `add` with your new options.

## New Features

See the Github [project page](https://github.com/r-spacex/SpaceXLaunchBot/projects/1) for planned updates.

If you want to request a feature, [open an issue](https://github.com/r-spacex/SpaceXLaunchBot/issues/new).
