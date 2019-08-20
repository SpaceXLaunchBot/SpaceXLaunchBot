import discord

import statics


def test_embeds():
    assert isinstance(statics.API_ERROR_EMBED, discord.Embed)
    assert isinstance(statics.DB_ERROR_EMBED, discord.Embed)
    assert isinstance(statics.GENERAL_ERROR_EMBED, discord.Embed)
    assert isinstance(statics.HELP_EMBED, discord.Embed)
    assert isinstance(statics.NEXT_LAUNCH_ERROR_EMBED, discord.Embed)
