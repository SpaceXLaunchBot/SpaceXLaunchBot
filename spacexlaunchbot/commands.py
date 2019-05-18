import config, embedcreators, statics
from redisclient import redis
from apis import spacex


async def handleCommand(client, message, is_owner, is_admin):

    # Info command

    if message.content.startswith("nextlaunch"):
        next_launch_dict = await spacex.get_next_launch_dict()
        if next_launch_dict == -1:
            launch_info_embed = statics.api_error_embed
        else:
            launch_info_embed = await embedcreators.get_launch_info_embed(
                next_launch_dict
            )
        await client.safe_send(message.channel, launch_info_embed)

    # Add/remove channel commands

    elif is_admin and message.content.startswith("addchannel"):
        reply = "This channel has been added to the notification service"
        added = await redis.sadd(
            "slb.subscribed_channels", str(message.channel.id).encode("UTF-8")
        )
        if added == 0:
            reply = "This channel is already subscribed to the notification service"
        await client.safe_send(message.channel, reply)

    elif is_admin and message.content.startswith("removechannel"):
        reply = "This channel has been removed from the launch notification service"
        removed = await redis.srem(
            "slb.subscribed_channels", str(message.channel.id).encode("UTF-8")
        )
        if removed == 0:
            reply = "This channel was not previously subscribed to the launch notification service"
        await client.safe_send(message.channel, reply)

    # Add/remove mention commands

    elif is_admin and message.content.startswith("setmentions"):
        reply = "Invalid input for setmentions command"
        roles_to_mention = " ".join(message.content.split("setmentions")[1:])
        if roles_to_mention.strip() != "":
            reply = f"Added notification ping for mentions(s): {roles_to_mention}"
            await redis.set_guild_mentions(message.guild.id, roles_to_mention)
        await client.safe_send(message.channel, reply)

    elif is_admin and message.content.startswith("removementions"):
        reply = "Removed mentions succesfully"

        deleted = await redis.delete_guild_mentions(message.guild.id)
        if deleted == 0:
            reply = "This guild has no mentions to be removed"

        await client.safe_send(message.channel, reply)

    elif is_admin and message.content.startswith("getmentions"):
        reply = "This guild has no mentions set"

        mentions = await redis.get_guild_mentions(message.guild.id)
        if mentions:
            reply = f"Mentions for this guild: {mentions}"

        await client.safe_send(message.channel, reply)

    # Misc

    elif message.content.startswith("info"):
        info_embed = await embedcreators.get_info_embed()
        await client.safe_send(message.channel, info_embed)

    elif message.content.startswith("help"):
        await client.safe_send(message.channel, statics.help_embed)

    # Debugging

    elif is_owner and message.content.startswith("dbgls"):
        # DeBugLaunchingSoon - Send launching soon embed for prev launch
        next_launch_dict = await spacex.get_next_launch_dict(previous=True)
        lse = await embedcreators.get_launching_soon_embed(next_launch_dict)
        await client.safe_send(message.channel, lse)

    elif is_owner and message.content.startswith("resetnts"):
        # Reset notification_task_store to default values (triggers notifications)
        await redis.set_notification_task_store("False", statics.general_error_embed)
        await client.safe_send(message.channel, "Reset notification_task_store")

    elif is_owner and message.content.startswith("logdump"):
        # Reply with latest lines from bot.log
        log_message = "```\n{}```"

        with open(config.LOG_PATH, "r") as f:
            # Code block markdown in log_message takes up 7 of the 2k allowed chars
            log_content = f.read()[-(2000 - 7) :]

        await client.safe_send(message.channel, log_message.format(log_content))
