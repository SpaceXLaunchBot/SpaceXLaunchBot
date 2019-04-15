from modules import apis, embedGenerators, statics
from modules.redisClient import redisConn


async def handleCommand(client, message, userIsOwner, userIsAdmin):

    # Info command

    if message.content.startswith("nextlaunch"):
        nextLaunchJSON = await apis.spacexApi.getNextLaunchJSON()
        if nextLaunchJSON == -1:
            launchInfoEmbed = statics.apiErrorEmbed
        else:
            launchInfoEmbed = await embedGenerators.genLaunchInfoEmbeds(nextLaunchJSON)
        await client.safeSend(message.channel, launchInfoEmbed)

    # Add/remove channel commands

    elif userIsAdmin and message.content.startswith("addchannel"):
        reply = "This channel has been added to the notification service"
        added = await redisConn.sadd(
            "slb.subscribedChannels", str(message.channel.id).encode("UTF-8")
        )
        if added == 0:
            reply = "This channel is already subscribed to the notification service"
        await client.safeSend(message.channel, reply)

    elif userIsAdmin and message.content.startswith("removechannel"):
        reply = "This channel has been removed from the launch notification service"
        removed = await redisConn.srem(
            "slb.subscribedChannels", str(message.channel.id).encode("UTF-8")
        )
        if removed == 0:
            reply = "This channel was not previously subscribed to the launch notification service"
        await client.safeSend(message.channel, reply)

    # Add/remove ping commands

    elif userIsAdmin and message.content.startswith("addping"):
        reply = "Invalid input for addping command"
        rolesToMention = " ".join(message.content.split("addping")[1:])
        if rolesToMention.strip() != "":
            reply = f"Added launch notification ping for mentions(s): {rolesToMention}"
            await redisConn.setGuildMentions(message.guild.id, rolesToMention)
        await client.safeSend(message.channel, reply)

    elif userIsAdmin and message.content.startswith("removeping"):
        reply = "Removed ping succesfully"

        guildMentionsDBKey = f"slb.{str(message.guild.id)}"
        deleted = await redisConn.delete(guildMentionsDBKey)

        if deleted == 0:
            reply = "This server has no pings to be removed"

        await client.safeSend(message.channel, reply)

    # Misc

    elif message.content.startswith("info"):
        await client.safeSend(message.channel, statics.infoEmbed)
    elif message.content.startswith("help"):
        await client.safeSend(message.channel, statics.helpEmbed)

    # Debugging

    elif userIsOwner and message.content.startswith("dbgls"):
        # DeBugLaunchingSoon - Send launching soon embed for prev launch
        nextLaunchJSON = await apis.spacexApi.getNextLaunchJSON(previous=True)
        lse = await embedGenerators.genLaunchingSoonEmbed(nextLaunchJSON)
        await client.safeSend(message.channel, lse)

    elif userIsOwner and message.content.startswith("resetnts"):
        # Reset notificationTaskStore to default values (triggers notifications)
        await redisConn.setNotificationTaskStore("False", statics.generalErrorEmbed)
        await client.safeSend(message.channel, "Reset notificationTaskStore")
