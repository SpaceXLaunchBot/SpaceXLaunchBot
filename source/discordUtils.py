from spacexAPI import generalErrorEmbed
from discord import errors

async def safeSendText(client, channel, message):
    """
    Send a text message to a client, and if an error occurs,
    safely supress it
    Returns 0 on error
    """
    try:
        return await client.send_message(channel, message)
    except errors.HTTPException:
        return 0  # API down, Message too big, etc.
    except errors.Forbidden:
        return 0  # No permission to message this channel

async def safeSendEmbed(client, channel, embed):
    """
    Send an embed to a client, and if an error occurs, safely
    supress it
    Returns 0 on error
    """
    try:
        return await client.send_message(channel, embed=embed)
    except errors.HTTPException:
        return 0
    except errors.Forbidden:
        return 0

async def safeSendLaunchInfoEmbeds(client, channel, embeds):
    """
    Specifically for sending 2 launch embeds, a full-detail one,
    and failing that, a "lite" version of the embed
    
    parameter $embeds:
        Should be as list of 2 embeds, one to attempt to send,
        and one that is garunteed to be under the character
        limit, to send if the first one is too big.
        It could also be a list with just 1 embed, but if this
        is over the char limit, nothing will happen.
        Other errors are automatically handled
    
    Returns 0 if both fail to send
    """
    for embed in embeds:
        try:
            return await client.send_message(channel, embed=embed)
        except errors.HTTPException:
            pass
        except errors.Forbidden:
            return 0  # No permissions to message this channel
    return await safeSendEmbed(client, channel, generalErrorEmbed)
