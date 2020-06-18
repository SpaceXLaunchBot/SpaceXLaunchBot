import asyncio
import datetime
import logging

import discord
from dictdiffer import diff

from . import apis
from . import config
from . import embeds

ONE_MINUTE = 60
LAUNCHING_SOON_DELTA = datetime.timedelta(minutes=config.NOTIF_TASK_LAUNCH_DELTA)


def get_embed_dict_differences(embed1: dict, embed2: dict) -> list:
    """Finds any differences between 2 embed dicts, returning the names of the keys /
    fields that are different. Does not find additions or deletions, just changes.

    Args:
        embed1: A dict of a discord Embed object.
        embed2: A dict of a discord Embed object.

    Returns:
        A List of strings that are the names of the changed keys / fields.

    """
    changes = []

    for difference in list(diff(embed1, embed2)):

        # The first index is the type of diff. We are looking for changes.
        if difference[0] == "change":
            if difference[1] == "image.url":
                # Ignore image url changes.
                continue

            # The second index ([1]) is the key, or in the case of fields, it is a list
            # like: ['fields', 0, 'value'].
            # Here we check it is a fields value that has changed, otherwise ignore it.
            if (
                isinstance(difference[1], list)
                and difference[1][0] == "fields"
                and difference[1][2] == "value"
            ):
                # diff[1][1] is the fields index in the embed dict.
                changes.append(embed1["fields"][difference[1][1]]["name"])

            else:
                changes.append(difference[1])

    return changes


async def _check_and_send_notifs(client: discord.Client) -> None:
    """Checks what notification messages need to be sent, and sends them.

    Updates database values if they need updating.

    Args:
        client : The Discord client to use to send messages.

    """
    next_launch_dict = await apis.spacex.get_launch_dict()

    # If the API is misbehaving, don't do anything, don't risk sending incorrect data
    if next_launch_dict == {}:
        return

    # Shortened to save space, ls = launching soon, li = launch information
    ls_notif_sent, old_li_embed_dict = client.ds.get_notification_task_vars()
    new_li_embed = await embeds.create_launch_info_embed(next_launch_dict)
    new_li_embed_dict = new_li_embed.to_dict()

    # This is the embed that will be saved to the notification task store
    embed_dict_to_save = old_li_embed_dict

    # Send out a launch information embed if it has changed from the previous one
    if new_li_embed_dict != old_li_embed_dict:
        logging.info("Launch info changed, sending notifications")

        # Get changes between old and new launch information embeds
        changes = get_embed_dict_differences(new_li_embed_dict, old_li_embed_dict)
        logging.info(f"Found changes: {changes}")

        # Deal with changes
        if len(changes) > 1:
            changed_text = f"Changed: {changes[0]} + {len(changes) - 1} more"
        elif len(changes) == 0:
            # It can be 0 if we use reset nts and the li embed dict is set to {}
            # The changes will be listed as "add" instead of "change" by dictdiffer
            changed_text = "Changed: New Embed"
        else:
            changed_text = f"Changed: {changes[0]}"

        new_li_embed.set_footer(text=changed_text)
        await client.send_all_subscribed(new_li_embed)

        ls_notif_sent = False
        embed_dict_to_save = new_li_embed_dict
    try:
        launch_timestamp = int(next_launch_dict["launch_date_unix"])
    except ValueError:
        # Doesn't have a date, don't trigger notifications
        launch_timestamp = 0

    current_time = datetime.datetime.utcnow()
    curr_time_plus_delta = (current_time + LAUNCHING_SOON_DELTA).timestamp()

    # Send out a launching soon notification if these criteria are met:
    # If the launch time is within the next NOTIF_TASK_LAUNCH_DELTA, and if the
    # launch_timestamp is not in the past, and we haven't already sent the notif
    if (
        curr_time_plus_delta >= launch_timestamp >= current_time.timestamp()
        and ls_notif_sent is False
    ):
        logging.info("Launch is soon, sending out notifications")
        launching_soon_embed = await embeds.create_launching_soon_embed(
            next_launch_dict
        )
        await client.send_all_subscribed(launching_soon_embed, True)
        ls_notif_sent = True

    # Save any changed data to db
    client.ds.set_notification_task_vars(ls_notif_sent, embed_dict_to_save)
    client.ds.save()


async def notification_task(client: discord.Client) -> None:
    """An async task to send out launching soon & launch info notifications."""
    await client.wait_until_ready()
    logging.info("Starting")

    while not client.is_closed():
        await _check_and_send_notifs(client)
        await asyncio.sleep(ONE_MINUTE * config.NOTIF_TASK_API_INTERVAL)
