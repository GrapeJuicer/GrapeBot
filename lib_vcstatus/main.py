import multiprocessing
import sys
# sys.path.append("..")  # .../discordbot/vcstatus で実行されたとき
sys.path.append(".")  # .../discordbot で実行されたとき

import os
import discord as dc
from sqlaccess.sqlaccess import SqliteAccessor
import lib_vcstatus.vcstatus as vc


vsDbName = "vcstatus.db"
vsTableName = "vcstatus"


intents: dc.Intents = dc.Intents.all()
client: dc.Client = dc.Client(intents=intents)

# get database file path
filepath = os.path.dirname(__file__) + os.sep + vsDbName
# connect database
vcdata = SqliteAccessor(filepath)


# call command
gbauth = [
    "!gb",
    "!grape",
    "!grapebot"
]


@client.event
async def on_ready():
    # update
    for guild in client.guilds:
        await vc.updateVcStatus(guild, vcdata, vsTableName)


@client.event
async def on_message(message: dc.Message):
    # do not anything if sender is this bot
    if message.author == client.user or message.content == "":
        return

    try:
        msg = message.content
        callcmd = msg[:msg.index(" ")]
    except ValueError:
        return

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
    if (messages[1] == "vclist"):  # voice channel list
        # send message and get sended message object
        msg = await vc.sendVcStatus(message.channel)
        # add message id to database
        vc.addVcStatusMessageId(msg, vcdata, vsTableName)
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
    else:
        raise Exception("NonMatchException")


# send error message to discord
async def sendErr(message: dc.Message):
    messages: list = [i for i in message.content.split(" ") if i != ""]
    str = "Invalid Usage.\n"
    str += "'" + " ".join(messages) + "' is not exist.\n"
    str += "Please enter '{0} help'.".format(messages[0])
    await message.channel.send(str)


# main
f = open("token.txt")
client.run(f.read())
