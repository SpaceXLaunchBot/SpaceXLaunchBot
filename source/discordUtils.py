from discord import errors

from errors import generalErrorEmbed

async def safeSendText(client, channel, message):
    """
    Send a text message to a client, and if an error occurs,
    safely supress it
    On failure, returns:
         0 : HTTPException
        -1 : Forbidden
        -2 : InvalidArgument
    """
    try:
        return await client.send_message(channel, message)
    except errors.HTTPException:
        return 0  # API down, Message too big, etc.
    except errors.Forbidden:
        return -1  # No permission to message this channel
    except errors.InvalidArgument:
        return -2  # Invalid channel ID

async def safeSendEmbed(client, channel, embed):
    """
    Send an embed to a client, and if an error occurs, safely
    supress it
    On failure, returns:
         0 : HTTPException
        -1 : Forbidden
        -2 : InvalidArgument
    """
    try:
        return await client.send_message(channel, embed=embed)
    except errors.HTTPException:
        return 0
    except errors.Forbidden:
        return -1
    except errors.InvalidArgument:
        return -2

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
    
    Returns 0 if neither embeds are sent
    """
    for embed in embeds:
        v = await safeSendEmbed(client, channel, embed)
        if v == 0:
            pass  # Embed might be too big, try lite version
        elif v == -1 or v == -2:
            return 0
        else:
            return v
    await safeSendEmbed(client, channel, generalErrorEmbed)
    return 0
