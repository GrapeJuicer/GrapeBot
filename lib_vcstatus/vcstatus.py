"""
TODO
- メッセージの更新
    - 更新時に追加されるユーザの名前が "None" になっている問題を修正
- リアクションの表示と反応に対する設定
- メッセージ削除時に "VC Status" メッセージであれば DB から削除する
- チャンネル名＋カテゴリ名からチャンネルオブジェクトを取得できないので，メッセージにIDを記載する
"""

from enum import unique
import sys

# sys.path.append("..")  # .../discordbot/vcstatus で実行されたとき
sys.path.append(".")  # .../discordbot で実行されたとき

import discord as dc
import sqlite3
from sqlaccess.sqlaccess import SqliteAccessor
from typing import Union
from NumCompression.numcom import numcom


alphaEmojis = ("🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯", "🇰", "🇱", "🇲", "🇳", "🇴", "🇵", "🇶", "🇷", "🇸", "🇹", "🇺", "🇻", "🇼", "🇽", "🇾", "🇿")


"""
def list2dict(li: list) ->dict:
    di = {}
    for l in li:
        if not l[0] in di:
            di[l[0]] = [l[1]]
        elif not l[1] in di[l[0]]:
            di[l[0]].append(l[1])
    return di


def dict2list(di: dict) -> list:
    li = []
    for k, v in di.items():
        for vi in v:
            li.append([k, vi])
    return li
"""


class ResizableEmbed(dc.Embed):
    def __init__(self, size: int, **kwargs):
        kwargs["title"] = kwargs.get('title', dc.embeds.EmptyEmbed) + " [{0}]".format(size if size <= 26 else "26+")
        super().__init__(**kwargs)
        self.size = size
    
    # return number of active VC. if value is larger than 
    @staticmethod
    def getSizeFromEmbed(embed :dc.Embed):
        if not type(embed.title) is str:
            return
        t: str = embed.title
        ifrom = t.rindex("[")
        ito = t.rindex("]")
        sval = t[ifrom+1:ito]
        if sval[-1] == "+":
            sval = sval[:-1]
        return int(sval)


# messageid ... integer or list of integer
def addVcStatusMessageId(message: dc.Message, accr: SqliteAccessor, table: str):
    # add item
    sql = "insert into {0} (guildid, channelid, msgid) values (?,?,?)".format(table)
    accr.execute(sql, [message.guild.id, message.channel.id, message.id])


def getActiveVc(guild: dc.Guild) -> list:
    # ボイスチャンネルの取得
    chs = [i for i in guild.channels if type(i) == dc.VoiceChannel]

    # for i in chs:
    #     getVcInfo(i)

    # アクティブなボイスチャンネルを抽出
    active_chs = [i for i in chs if len(i.members) > 0]

    # Discordでの表示順に並び替え
    active_chs = sorted(active_chs, key=lambda f: f.position)

    return active_chs


def getVcMembersAsString(channel: dc.VoiceChannel, head="", end="", div=" ") -> str:
    s: str = head

    for m in channel.members:
        if m.nick == None:
            s += str(m.name) + div
        else:
        s += str(m.nick) + div

    return s[:-len(div)] + end  # 最後の1文字以外を返す


def getVcInfo(channel: dc.VoiceChannel) -> None:
    print("--------------------------------")
    print("作成日時      : {0}".format(str(channel.created_at)))
    print("ビットレート  : {0}".format(channel.bitrate))
    print("サーバー      : {0}".format(channel.guild.name))
    print("カテゴリ (ID) : {0} ({1})".format(channel.category, channel.category_id))
    print("ID            : {0}".format(channel.id))
    print("チャンネル名  : {0}".format(channel.name))
    print("メンバー      : {0}".format([i.name for i in channel.members]))
    print("メンバー数    : {0}".format(len(channel.members)))


# return embed as following field type: "channel.name [category.name]"
def getVcStatusEmbed(guild: dc.Guild) -> ResizableEmbed:
    # get active voice channel list
    vclist = getActiveVc(guild)
    # get active voice num
    num = len(vclist)
    # get embed obect with title message
    embed: ResizableEmbed = ResizableEmbed(min(num, 26), title="Voice Channel Status", color=0xa652bb)
    # voice channel is exist
    if num > 0:
        for i, ch in enumerate(vclist):
            if i > 25:  # after than 'z'
                embed.add_field(name="etc...", value="Too many active VC !", inline=False)
            break
            # set channel name
            name = alphaEmojis[i] + " " + ch.name
            # set category name if channel's category is exist
            if ch.category != None:
                name += " [%s]" % ch.category.name
            # convert id from int to numcom
            ncid = numcom(ch.id)
            # set channelid
            name += " (%s)" % ncid
            # set embed's user list header
            lh = "---- "
            # get voice channel members as string
            val = getVcMembersAsString(ch, head=lh, div="\n" + lh)
            # add field
            embed.add_field(name=name, value=val, inline=False)
            # increment
            i += 1
    # not exist
    else:
        embed.add_field(name="None", value="---- No VC is active.", inline=False)
    # return embed object
    return embed


async def sendVcStatus(channel: dc.TextChannel) -> dc.Message:
    # get voice channel status of the guild
    embed: ResizableEmbed = getVcStatusEmbed(channel.guild)
    # send message and get message object
    msg = await channel.send(embed=embed)
    # add reaction
    await addStatusReaction(msg, embed.size)
    # return message's object
    return msg


# table : vcstatus (guildid, msgid)
def isVcStatusMessage(message: dc.Message, accr: SqliteAccessor, table: str) -> bool:
    sql = "select guildid, channelid, msgid from {0} where guildid = {1} and channelid = {2} and msgid = {3}"\
                    .format(table, message.guild.id, message.channel.id, message.id)
    # execute sql command
    accr.execute(sql)
    # return
    return len(accr.fetchall()) > 0  # exist...True, none...False


async def updateVcStatusMessage(message: dc.Message, accr: SqliteAccessor, table: str)-> None:
    # check message
    if not isVcStatusMessage(message, accr, table):
        return
    # get old embed
    oldembed: dc.Embed = message.embeds[0]
    # get size if old embed
    osize = ResizableEmbed.getSizeFromEmbed(oldembed)
    # create embed of voice chat status
    embed: ResizableEmbed = getVcStatusEmbed(message.guild)
    # edit message
    await message.edit(embed=embed)
    # update reaction
    await updateStatusReaction(message, osize, embed.size)


async def addStatusReaction(message: dc.Message, num: int) -> None:
    # check value
    if num > 26:
        raise Exception("ValueError")
    # add reaction
    for i in range(0, num):
        await message.add_reaction(alphaEmojis[i])


async def updateStatusReaction(message: dc.Message, osize: int, nsize: int) -> None:
    if osize < nsize:
        for i in range(osize, nsize):
            await message.add_reaction(alphaEmojis[i])
    elif osize > nsize:
        for i in range(nsize, osize):
            await message.clear_reaction(alphaEmojis[i])


