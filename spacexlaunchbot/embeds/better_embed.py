from typing import Union

import discord


class BetterEmbed(discord.Embed):
    def __init__(
        self,
        fields: Union[None, list[list[str]]] = None,
        footer: Union[None, str] = None,
        inline_fields: bool = True,
        **kwargs,
    ):
        """Extends the discord.Embed class with more functionality.

        Args:
            fields: A list of pairs of strings, the name and text of each field.
            footer: The footer.
            inline_fields: Whether or not to inline all of the fields.

        """
        super().__init__(**kwargs)
        if fields is not None:
            for field in fields:
                self.add_field(name=field[0], value=field[1], inline=inline_fields)
        if footer is not None:
            self.set_footer(text=footer)

    def size_ok(self) -> bool:
        """Determines if an embed is within the size limits for discord.

        See https://discord.com/developers/docs/resources/channel#embed-limits

        Returns:
            True if it is within size limits, otherwise False.

        """
        if len(self.fields) > 25:
            return False

        total_len = 0
        comparisons = []

        if self.title is not None:
            comparisons.append([len(self.title), 256])  # type: ignore

        if self.description is not None:
            comparisons.append([len(self.description), 2048])  # type: ignore

        if self.author.name is not None:
            comparisons.append([len(self.author.name), 256])  # type: ignore

        if self.footer is not None:
            comparisons.append([len(self.footer), 2048])  # type: ignore

        for length, limit in comparisons:
            if length > limit:
                return False
            total_len += length

        for field in self.fields:
            name_length = len(field.name)  # type: ignore
            value_length = len(field.value)  # type: ignore
            if name_length > 256 or value_length > 1024:
                return False

            total_len += name_length + value_length

        if total_len > 6000:
            return False

        return True
