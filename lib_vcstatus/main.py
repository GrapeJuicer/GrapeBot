import multiprocessing
import sys

sys.path.append("..")  # .../discordbot/vcstatus で実行されたとき
sys.path.append(".")  # .../discordbot で実行されたとき

import os
import discord as dc
from sqlaccess.sqlaccess import SqliteAccessor
import lib_vcstatus.vcstatus as vc
import processflag.pflag as pf


vsDbName = "vcstatus.db"
vsTableName = "vcstatus"


intents: dc.Intents = dc.Intents.all()
client: dc.Client = dc.Client(intents=intents)

# get database file path
filepath = os.path.abspath(os.path.dirname(__file__)) + os.sep + vsDbName
# connect database
vcdata = SqliteAccessor(filepath)

# multi-process var
activeProcessFlag: multiprocessing.Value
flagMP = False

# call command
gbauth = [
    "!gb",
    "!grape",
    "!grapebot"
]


@client.event
async def on_ready():
    # set flag or disp messsage
    if flagMP:
        activeProcessFlag.value = pf.ACTIVE
    else:
        print("'vcstatus' module ready. (user: {0}, id: {1})".format(client.user.name, client.user.id))
    
    # update
    for guild in client.guilds:
        await vc.updateVcStatus(guild, vcdata, vsTableName)


@client.event
async def on_message(message: dc.Message):
    # do not anything if sender is this bot
    if message.author == client.user or message.guild is None:
        return
    
    msg = message.content
    idx = msg.find(" ")
    if idx == -1:
        return

    # get cmd
    callcmd = msg[:idx]
    
    # if message uses command that calls this bot
    if callcmd in gbauth:
        try:
            # message processing func
            await messageProcess(message)
        except:
            # error
            await sendErr(message)


# message processing
async def messageProcess(message: dc.Message):
    # convert a space-separated string to a list
    messages: list = [i for i in message.content.split(" ") if i != ""]
    # check
    if messages[1:3] == ["vcstatus", "list"] and message.author.guild_permissions.administrator: # voice channel list
        # send message and get sended message object
        msg = await vc.sendVcStatus(message.channel)
        # add message id to database
        vc.addVcStatusMessageId(msg, vcdata, vsTableName)

    elif messages[1] == "close" and "vcstatus" in messages[2:]:
        if message.author.permissions_in(message.channel).administrator:
            await message.channel.send("LOG: 'vcstatus' process was closed")
            # print("'vcstatus' process was closed")
            await client.close()

    # elif (messages[1] == "join"):
    #     # check
    #     if message.author.voice is None:
    #         await message.channel.send("You should join voice channel !")
    #         return
    #     # connect
    #     await message.author.voice.channel.connect()
    # elif (messages[1] == "leave"):
    #     # check
    #     if message.guild.voice_client is None:
    #         await message.channel.send("You should join voice channel !")
    #         return
    #     # disconnect
    #     await message.guild.voice_client.disconnect()
    elif messages[1] == "vcstatus":
        raise Exception("NonMatchException")


@client.event
async def on_voice_state_update(member: dc.Member, before: dc.VoiceState, after: dc.VoiceState):
    await vc.updateVcStatus(member.guild, vcdata, vsTableName)


@client.event
async def on_raw_reaction_add(payload: dc.RawReactionActionEvent):
    # check reaction type
    if payload.event_type != "REACTION_ADD" or payload.member == client.user:
        return
    # get channel object
    channel = client.get_channel(payload.channel_id)
    # check channel type
    if type(channel) != dc.TextChannel:
        return
    # get message objct
    message: dc.Message = await channel.fetch_message(payload.message_id)
    # don't do anything if sender is me
    if not vc.isVcStatusMessage(message, vcdata, vsTableName):
        return
    # remove reaction
    await message.remove_reaction(payload.emoji, payload.member)
    # create invate
    try:
        inv: dc.Invite = await vc.getVcInvite(message, payload.emoji)
        # send invite link
        await payload.member.send("This is your invite link of voice channel:\nURL: %s" % inv.url)
    except:
        # there's nothing to do at the moment.
        pass


# send error message to discord
async def sendErr(message: dc.Message):
    messages: list = [i for i in message.content.split(" ") if i != ""]
    str = "Invalid Usage.\n"
    str += "'" + " ".join(messages) + "' is not exist.\n"
    str += "Please enter '{0} help'.".format(messages[0])
    await message.channel.send(str)


@client.event
async def on_raw_message_delete(payload: dc.RawMessageDeleteEvent):
    vcdata.execute("delete from {0} where guildid = {1} and channelid = {2} and msgid = {3}"\
                    .format(vsTableName, payload.guild_id, payload.channel_id, payload.message_id))


def launch_vcstatus(token: str, activeFlag: multiprocessing.Value = None):
    # set flag
    if not activeFlag == None:
        global activeProcessFlag
        global flagMP
        activeProcessFlag = activeFlag
        activeProcessFlag.value = pf.LAUNCHING
        flagMP = True
    
    # execute command - create table
    vcdata.execute("create table if not exists {0}(guildid, channelid, msgid)".format(vsTableName))
    # run
    client.run(token)
    
    # disconnect database
    vcdata.disconnect()

    # set flag
    if not activeFlag == None:
        activeProcessFlag.value = pf.INACTIVE


# main ---
if __name__ == "__main__":
    with open("../token.txt") as f:
        launch_vcstatus(f.read())
