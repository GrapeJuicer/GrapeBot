import multiprocessing
import sys
# sys.path.append("..")  # .../discordbot/vcstatus で実行されたとき
sys.path.append(".")  # .../discordbot で実行されたとき

import os
import discord as dc
from sqlaccess.sqlaccess import SqliteAccessor
import lib_vcstatus.vcstatus as vc



intents: dc.Intents = dc.Intents.all()
client: dc.Client = dc.Client(intents=intents)


# call command
gbauth = [
    "!gb",
    "!grape",
    "!grapebot"
]


@client.event
async def on_ready():
    print("Logged in as")
    print("User : ", client.user.name)
    print("ID   : ", client.user.id)
    print("------")


@client.event
async def on_message(message: dc.Message):
    # do not anything if sender is this bot
    if message.author == client.user or message.content == "":
        return

    # convert a space-separated string to a list
    msgs = message.content.split(" ")
    # remove empty string in message list
    msgs = [i for i in msgs if i != ""]

    # if message uses command that calls this bot
    if msgs[0] in gbauth:
        try:
            # message processing func
            await messageProcess(msgs, message.channel)
        except:
            # error
            await sendErr(msgs, message.channel)


# message processing
async def messageProcess(messages: list, channel: dc.TextChannel):
    if (messages[1] == "vclist"):  # voice channel list -------------------------
        await vc.sendVcStatus(channel)
    else:
        raise Exception("NonMatchException")


# send error message to discord
async def sendErr(messages: list, channel: dc.TextChannel):
    str = "Invalid Usage.\n"
    str += "'" + " ".join(messages) + "' is not exist.\n"
    str += "Please enter '{0} help'.".format(messages[0])
    await channel.send(str)


# main
f = open("token.txt")
client.run(f.read())
