from discord import Interaction, Embed, SelectOption, Message, Emoji, PartialEmoji, Colour
from discord.ui import TextInput, Button, Modal, View, Select
from discord.enums import ButtonStyle
from ..base import *
from discord.utils import MISSING
from sqlite3 import Connection
from datetime import datetime

def init(connection: Connection):
    cur = connection.cursor()
    cur.execute('create table if not exists gb_vote(id int primary key, date datetime not null, guild_id int not null, message_id int not null, user_id text not null, choice int not null)')
    connection.commit()
    cur.close()



class VoteModal(Modal):
    t1 = TextInput(label='選択肢1')
    t2 = TextInput(label='選択肢2')
    t3 = TextInput(label='選択肢3', required=False, placeholder='（任意）')
    t4 = TextInput(label='選択肢4', required=False, placeholder='（任意）')
    t5 = TextInput(label='選択肢5', required=False, placeholder='（任意）')

    def __init__(self, *, title: str = '投票', timeout: Optional[float] = None, custom_id: str = MISSING, visible: str = 'Yes') -> None:
        super().__init__(
            title=title,
            timeout=timeout,
            custom_id=custom_id
        )

        self.visible = visible == 'Yes'

    async def on_submit(self, interaction: Interaction) -> None:
        choices = [self.t1.value, self.t2.value,
                   self.t3.value, self.t4.value, self.t5.value]
        choices = list(filter(lambda x: x != '', choices))

        desc = '\n'.join([
            '**%s**' % self.title,
            '*cteated by* %s' % interaction.user.mention,
            ''
        ] + [
            '**%d.** %s' % (i + 1, c) for i, c in enumerate(choices)
        ])
        embed_top = Embed(title='公開投票' if self.visible else '匿名投票', description=desc, colour=Colour.blue())

        embed_status = Embed(title='投票済みメンバー 一覧', colour=Colour.dark_blue())


        def checker(interaction: Interaction):
            from main import connection
            cur = connection.cursor()
            cur.execute('select 0 from gb_vote where guild_id = ? and message_id = ? and user_id = ?', [interaction.guild.id, interaction.message.id, interaction.user.id])
            return len(cur.fetchall()) == 0

        await interaction.response.send_message(embeds=[embed_top, embed_status], view=ExtView([
            ResponseButton(
                style=ButtonStyle.primary,
                label='投票する',
                content='投票は**1回**のみ可能です\n投票後の再投票はできません',
                view=ExtView([
                    VoteSelect(
                        placeholder='選択してください',
                        options=[
                            SelectOption(label=c, value=i, description='選択肢 %d' % (i + 1)) for i, c in enumerate(choices)
                        ]
                    )
                ]),
                ephemeral=True,
                checker=checker,
                ignore_message='投票済みです',
                emoji=PartialEmoji(name='🗳️'),
            ),
            VoteEndButton(
                style=ButtonStyle.danger,
                label='投票終了',
                owner=interaction.user.id,
                emoji=PartialEmoji(name='🔚'),
                selection=choices,
                visible=self.visible,
            ),
        ]))



class VoteSelect(Select):
    def __init__(
        self,
        *,
        custom_id: str = MISSING,
        placeholder: Optional[str] = None,
        min_values: int = 1,
        max_values: int = 1,
        options: list[SelectOption] = MISSING,
        disabled: bool = False,
        row: Optional[int] = None
        ) -> None:

        super().__init__(
            custom_id=custom_id,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            options=options,
            disabled=disabled,
            row=row
        )

    async def callback(self, interaction: Interaction):
        from main import connection

        cur = connection.cursor()
        cur.execute('select 0 from gb_vote where guild_id = ? and message_id = ? and user_id = ?', [interaction.guild.id, interaction.message.reference.message_id, interaction.user.id])
        r = len(cur.fetchall()) == 0

        if r:
            # already voted
            cur.execute(
                'insert into gb_vote (date, guild_id, message_id, user_id, choice) values (?, ?, ?, ?, ?)',
                (
                    datetime.now(),
                    interaction.guild.id,
                    interaction.message.reference.message_id,
                    interaction.user.id,
                    int(self.values[0]),
                )
            )
            connection.commit()

        cur.close()

        if r:
            titlemsg: Message = await interaction.channel.fetch_message(interaction.message.reference.message_id)
            embeds = titlemsg.embeds
            embeds[1].description = f'> {interaction.user.mention}' if embeds[1].description is None else f'{embeds[1].description}\n> {interaction.user.mention}'
            await titlemsg.edit(embeds=embeds)
            await interaction.response.send_message('投票しました', ephemeral=True)
        else:
            await interaction.response.send_message('投票済みです', ephemeral=True)



class VoteEndButton(Button):
    def __init__(
        self,
        *,
        owner: int,
        selection: list[str],
        style: ButtonStyle = ButtonStyle.secondary,
        label: Optional[str] = None,
        disabled: bool = False,
        custom_id: Optional[str] = None,
        url: Optional[str] = None,
        emoji: Optional[Union[str, Emoji, PartialEmoji]] = None,
        row: Optional[int] = None,
        visible: bool = True,
    ):
        super().__init__(
            style=style,
            label=label,
            disabled=disabled,
            custom_id=custom_id,
            url=url,
            emoji=emoji,
            row=row
        )

        self.owner = owner
        self.selection = selection
        self.visible = visible

    async def callback(self, interaction: Interaction):
        # auth
        if interaction.user.guild_permissions.administrator or interaction.user.id == self.owner:
            from main import connection
            cur = connection.cursor()
            cur.execute('select user_id, choice from gb_vote where guild_id = ? and message_id = ?', [interaction.guild.id, interaction.message.id])
            result = cur.fetchall()
            cur.close()

            # array[Vote No.] -> user list
            result_map = [list(map(lambda x: x[0], filter(lambda x: x[1] == i, result))) for i in range(len(self.selection))]
            select_map = []

            for i, s in enumerate(self.selection):
                users = []
                for x in result_map[i]:
                    users.append(await interaction.guild.fetch_member(x))
                select_map.append([s, users])

            select_map.sort(key=lambda x: len(x[1]), reverse=True)

            embed_result: Embed = Embed(title='投票結果', description='\n'.join([('**%d位** : %s (%d票)' % (i + 1, x[0], len(x[1]))) for i, x in enumerate(select_map)]), colour=Colour.red())
            embed_where: Embed = Embed(
                title='投票先',
                description='\n'.join(
                    list(map(
                        lambda x: '**%s** -----\n%s' % (x[0], '\n'.join(list(map(lambda y: str(y.mention), x[1]))) if x[1] else 'なし')
                        , select_map
                    ))
                ),
                colour=Colour.gold()
            )

            embeds: list = interaction.message.embeds

            embeds[1] = embed_result

            if self.visible:
                embeds.append(embed_where)

            await interaction.message.edit(embeds=embeds, view=None)
        else:
            await interaction.response.send_message(content='投票を終了できるのは管理者または作成者のみです', ephemeral=True)
