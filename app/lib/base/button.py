from discord import Interaction, Embed
from discord.ui import Button, View
from discord.enums import ButtonStyle
from discord.emoji import Emoji
from discord.partial_emoji import PartialEmoji
from typing import Optional, Union
from discord.utils import MISSING


class ResponseButton(Button):
    def __init__(
        self,
        *,
        style: ButtonStyle = ButtonStyle.secondary,
        label: Optional[str] = None,
        disabled: bool = False,
        custom_id: Optional[str] = None,
        url: Optional[str] = None,
        emoji: Optional[Union[str, Emoji, PartialEmoji]] = None,
        row: Optional[int] = None,
        content: str = None,
        view: View = MISSING,
        embed: Embed = MISSING,
        ephemeral: bool = False,
        checker = None, # checker(interaction: discord.Interaction) -> PASS:True, IGNORE:False
        ignore_message = 'Your request has been ignored.',
        ):

        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row)

        self.user_content = content
        self.user_view = view
        self.user_embed = embed
        self.user_ephemeral = ephemeral
        self.checker = checker
        self.ignore_message = ignore_message


    async def callback(self, interaction: Interaction):
        if self.checker is not None and not self.checker(interaction):
            await interaction.response.send_message(
                content=self.ignore_message,
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                content=self.user_content,
                view=self.user_view,
                embed=self.user_embed,
                ephemeral=self.user_ephemeral
            )
