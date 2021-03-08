import discord as dc


def getActiveVc(guild: dc.Guild):
    chs = [i for i in guild.channels if type(i) == dc.VoiceChannel]

    # for i in chs:
    #     getVcInfo(i)

    active_chs = [i for i in chs if len(i.members) > 0]
    return active_chs


def getVcMembersAsString(channel: dc.VoiceChannel, head="", end="", div=" "):
    s: str = head

    for m in channel.members:
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
    embed: dc.Embed = dc.Embed(title="Voice Channel Status")
    vclist = getActiveVc(channel.guild)
    i = 97;
    for ch in vclist:
        if i > 122:  # chr(122) = 'z'
            embed.add_field(name="etc...", inline=False)
            break

        name = ":regional_indicator_" + chr(i) + ": " + ch.name
        embed.add_field(name=name, value=getVcMembersAsString(ch, head=" ---- ", div="\n ---- "), inline=False)
        i += 1

    await channel.send(embed=embed)
