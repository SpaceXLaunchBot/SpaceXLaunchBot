from spacexlaunchbot.embeds import BetterEmbed


def test_embed_is_valid():
    assert BetterEmbed().size_ok() is True
    assert BetterEmbed(title="a" * 256).size_ok() is True
    assert BetterEmbed(description="a" * 2048).size_ok() is True
    assert BetterEmbed(fields=[["a", "a"]] * 25).size_ok() is True


def test_embed_is_invalid():
    assert BetterEmbed(title="a" * 257).size_ok() is False
    assert BetterEmbed(description="a" * 2049).size_ok() is False
    assert BetterEmbed(fields=[["a", "a"]] * 26).size_ok() is False
