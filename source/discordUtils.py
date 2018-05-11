from api import generalErrorEmbed
from discord import errors

async def safeSendText(client, channel, message):
    """
    Send a text message to a client, and if an error occurs,
    safely supress it
    """
    try:
        return await client.send_message(channel, message)
    except errors.HTTPException:
        return  # API down, Message too big, etc.
    except errors.Forbidden:
        return  # No permission to message this channel

async def safeSendEmbed(client, channel, embeds):
    """
    General function for sending a channel the latest launch embed
    
    parameter $embeds:
        Should be as list of 2 embeds, one to attempt to send,
        and one that is garunteed to be under the character
        limit, to send if the first one is too big.
        It could also be a list with just 1 embed, but if this
        is over the char limit, nothing will happen.
        Other errors are automatically handled
    """
    for embed in embeds:
        try:
            return await client.send_message(channel, embed=embed)
        except errors.HTTPException:
            pass
        except (errors.Forbidden, errors.InvalidArgument):
            return  # No permission to message this channel, or this channel does not exist, stop trying
    await client.send_message(channel, embed=generalErrorEmbed)
