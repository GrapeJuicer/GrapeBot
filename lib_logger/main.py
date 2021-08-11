import multiprocessing
import sys
sys.path.append("..")  # .../discordbot/lib_logger で実行されたとき
sys.path.append(".")   # .../discordbot で実行されたとき

import os
import discord as dc
import processflag.pflag as pf
from sqlaccess.sqlaccess import SqliteAccessor
from typing import Any, Literal, Union
import datetime as dt
import lib_logger.DBmanager as dm
import lib_logger.logger as log


logDbName = "logger.db"
logTableName = "logger"


intents: dc.Intents = dc.Intents.all()
client: dc.Client = dc.Client(intents=intents)


# get database file path
filepath = os.path.abspath(os.path.dirname(__file__)) + os.sep + logDbName
# connect database
logdata = SqliteAccessor(filepath)


# multi-process var
activeProcessFlag: multiprocessing.Value
flagMP = False


# logging class
log_manager = log.DiscordLogging("GrapeBot")


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
        print("'logger' module ready. (user: {0}, id: {1})".format(client.user.name, client.user.id))

    # log
    # get guilds that use the logger module
    logdata.execute("select distinct guildid from {0}".format(logTableName))
    guilds = []
    for gid in logdata.fetchall(): # gid -> (id,)
        guilds.append(await client.fetch_guild(gid[0]))

    # log each guild
    for g in guilds:
        await loggingAll(g, log.EnumLog.ME_READY, None)


@client.event
async def on_typing(channel: dc.abc.Messageable, user: Union[dc.User, dc.Member], when: dt.datetime):
    # log
    await loggingAll(channel.guild, log.EnumLog.TYPING, [channel, user, when])


@client.event
async def on_message(message: dc.Message):
    if message.author == client.user or message.guild is None:
        return

    # log
    await loggingAll(message.guild, log.EnumLog.MESSAGE_SEND, message)
    
    # processing command below --------------------------------------------------------------------

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



async def loggingAll(guild: dc.Guild, type: Literal, data: Any):
    # get log cahnnels
    chs = await dm.getChannels(logdata, logTableName, guild)
    # logging
    for ch in chs:
        await log_manager.log(type, ch, data)


# message processing
async def messageProcess(message: dc.Message):
    # convert a space-separated string to a list
    msgs: list = [i for i in message.content.split(" ") if i != ""]
    
    # add log channel to DB
    if msgs[1:3] == ["logger", "add"] and message.author.guild_permissions.administrator:
        for ch in msgs[3:]:
            try:
                # get channel
                channel = message.channel if ch == "here" else client.get_channel(int(ch))
                # add channel to DB
                dm.addLogChannel(channel, logdata, logTableName)
            except:
                # channel-id contains character or channel doesn't exist
                await message.channel.send("Error:logger: Channel with {0} doesn't exists or isn't a text-channel-id.".format(ch))
            else: # if no exception is raised
                await channel.send("**NOTE**\nThis channel has been added to the log channel.\nIf you want to remove from the log channel, send `{0} logger remove <{1}/here>`.".format(gbauth[0], channel.id))
    
    # remove log channel from DB
    elif msgs[1:3] == ["logger", "remove"] and message.author.guild_permissions.administrator:
        for ch in msgs[3:]:
            try:
                # get channel
                channel = message.channel if ch == "here" else client.get_channel(int(ch))
                # remove channel from DB
                dm.removeLogChannel(channel,  logdata, logTableName)
            except:
                # channel-id contains character or channel doesn't exist
                await message.channel.send("Error:logger: Channel with {0} doesn't exists or isn't a text-channel-id.".format(ch))
            else: # if no exception is raised
                await channel.send("**NOTE**\nThis channel has been removed from the log channel.\nIf you want to add to the log channel, send `{0} logger add <{1}/here>`.".format(gbauth[0], channel.id))

    # get the ID of the channel that sent the message.
    elif msgs[1:] == ["logger", "id"]:
        await message.channel.send(str(message.channel.id))

    elif msgs[1] == "logger":
        raise Exception("NonMatchException")


# send error message to discord
async def sendErr(message: dc.Message):
    messages: list = [i for i in message.content.split(" ") if i != ""]
    str = "Invalid Usage.\n"
    str += "'" + " ".join(messages) + "' is not exist.\n"
    str += "Please enter '{0} help'.".format(messages[0])
    await message.channel.send(str)


# launcher
def launch_logger(token: str, activeFlag: multiprocessing.Value = None):
    # set flag
    if not activeFlag == None:
        global activeProcessFlag
        global flagMP
        activeProcessFlag = activeFlag
        activeProcessFlag.value = pf.LAUNCHING
        flagMP = True
    
    # create table
    logdata.execute("create table if not exists {0} (guildid, channelid)".format(logTableName))
    
    client.run(token)
    
    # set flag
    if not activeFlag == None:
        activeProcessFlag.value = pf.INACTIVE


# main ---
if __name__ == "__main__":
    with open("../token.txt") as f:
        launch_logger(f.read())
