from spacexlaunchbot import embeds

from discord import Embed


def test_embed_is_valid():
    assert embeds.embed_is_valid(Embed()) is True
    assert embeds.embed_is_valid(Embed(title="a" * 256)) is True
    assert embeds.embed_is_valid(Embed(description="a" * 2048)) is True
    assert (
        embeds.embed_is_valid(embeds.EmbedWithFields(fields=[["a", "a"]] * 25)) is True
    )


def test_embed_is_invalid():
    assert embeds.embed_is_valid(Embed(title="a" * 257)) is False
    assert embeds.embed_is_valid(Embed(description="a" * 2049)) is False
    assert (
        embeds.embed_is_valid(embeds.EmbedWithFields(fields=[["a", "a"]] * 26)) is False
    )
