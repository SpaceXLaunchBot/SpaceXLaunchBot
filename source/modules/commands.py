import config
from modules import apis, embedGenerators, statics
from modules.redis_client import redis


async def handleCommand(client, message, is_owner, is_admin):

    # Info command

    if message.content.startswith("nextlaunch"):
        next_launch_dict = await apis.SpacexApi.get_next_launch_dict()
        if next_launch_dict == -1:
            launch_info_embed = statics.apiErrorEmbed
        else:
            launch_info_embed = await embedGenerators.gen_launch_info_embeds(
                next_launch_dict
            )
        await client.safe_send(message.channel, launch_info_embed)

    # Add/remove channel commands

    elif is_admin and message.content.startswith("addchannel"):
        reply = "This channel has been added to the notification service"
        added = await redis.sadd(
            "slb.subscribedChannels", str(message.channel.id).encode("UTF-8")
        )
        if added == 0:
            reply = "This channel is already subscribed to the notification service"
        await client.safe_send(message.channel, reply)

    elif is_admin and message.content.startswith("removechannel"):
        reply = "This channel has been removed from the launch notification service"
        removed = await redis.srem(
            "slb.subscribedChannels", str(message.channel.id).encode("UTF-8")
        )
        if removed == 0:
            reply = "This channel was not previously subscribed to the launch notification service"
        await client.safe_send(message.channel, reply)

    # Add/remove mention commands

    elif is_admin and message.content.startswith("setmentions"):
        reply = "Invalid input for setmentions command"
        rolesToMention = " ".join(message.content.split("setmentions")[1:])
        if rolesToMention.strip() != "":
            reply = f"Added notification ping for mentions(s): {rolesToMention}"
            await redis.setGuildMentions(message.guild.id, rolesToMention)
        await client.safe_send(message.channel, reply)

    elif is_admin and message.content.startswith("removementions"):
        reply = "Removed mentions succesfully"

        guild_mentions_db_key = f"slb.{str(message.guild.id)}"
        deleted = await redis.delete(guild_mentions_db_key)

        if deleted == 0:
            reply = "This guild has no mentions to be removed"

        await client.safe_send(message.channel, reply)

    elif is_admin and message.content.startswith("getmentions"):
        reply = "This guild has no mentions set"

        mentions = await redis.getGuildMentions(message.guild.id)
        if mentions:
            reply = f"Mentions for this guild: {mentions}"

        await client.safe_send(message.channel, reply)

    # Misc

    elif message.content.startswith("info"):
        infoEmbed = await embedGenerators.getInfoEmbed()
        await client.safe_send(message.channel, infoEmbed)

    elif message.content.startswith("help"):
        await client.safe_send(message.channel, statics.helpEmbed)

    # Debugging

    elif is_owner and message.content.startswith("dbgls"):
        # DeBugLaunchingSoon - Send launching soon embed for prev launch
        next_launch_dict = await apis.SpacexApi.get_next_launch_dict(previous=True)
        lse = await embedGenerators.genLaunchingSoonEmbed(next_launch_dict)
        await client.safe_send(message.channel, lse)

    elif is_owner and message.content.startswith("resetnts"):
        # Reset notificationTaskStore to default values (triggers notifications)
        await redis.setNotificationTaskStore("False", statics.generalErrorEmbed)
        await client.safe_send(message.channel, "Reset notificationTaskStore")

    elif is_owner and message.content.startswith("logdump"):
        # Reply with latest lines from bot.log
        log_message = "```\n{}```"

        with open(config.LOG_PATH, "r") as f:
            # Code formatting in message takes up 7 of the 2k allowed chars
            logContent = f.read()[-(2000 - 7) :]

        await client.safe_send(message.channel, log_message.format(logContent))
