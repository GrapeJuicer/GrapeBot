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

def getActiveVc(guild: dc.Guild):
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


def getVcInfo(channel: dc.VoiceChannel):
    print("--------------------------------")
    print("作成日時      : {0}".format(str(channel.created_at)))
    print("ビットレート  : {0}".format(channel.bitrate))
    print("サーバー      : {0}".format(channel.guild.name))
    print("カテゴリ (ID) : {0} ({1})".format(channel.category, channel.category_id))
    print("ID            : {0}".format(channel.id))
    print("チャンネル名  : {0}".format(channel.name))
    print("メンバー      : {0}".format([i.name for i in channel.members]))
    print("メンバー数    : {0}".format(len(channel.members)))


async def sendVcStatus(channel: dc.TextChannel):
    embed: dc.Embed = dc.Embed(title="Voice Channel Status", color=0xa652bb)
    vclist = getActiveVc(channel.guild)
    i = 97;
    for ch in vclist:
        if i > 122:  # chr(122) = 'z'
            embed.add_field(name="etc...", inline=False)
            break
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


