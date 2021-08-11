import enum
from logging import exception
from sys import exec_prefix
import discord as dc
from discord import guild
from discord import client
from sqlaccess.sqlaccess import SqliteAccessor


def addLogChannel(channel: dc.TextChannel, db: SqliteAccessor, table_name: str):
    # check channel
    if channel is None or type(channel) != dc.TextChannel:
        raise TypeError
    # check if it is already registered in DB
    db.execute("select channelid from {0} where guildid = {1} and channelid = {2}".format(table_name, channel.guild.id, channel.id))
    if db.fetchall():
        raise Exception("DuplicateError")
    # add to DB
    db.execute("insert into {0} (guildid, channelid) values (?,?)".format(table_name), [channel.guild.id, channel.id])
    

def removeLogChannel(channel: dc.TextChannel, db: SqliteAccessor, table_name: str):
    # check channel
    if channel is None or type(channel) != dc.TextChannel:
        raise TypeError
    # check if it exists in the DB
    db.execute("select channelid from {0} where guildid = {1} and channelid = {2}".format(table_name, channel.guild.id, channel.id))
    if not db.fetchall():
        raise Exception("NonExistError")
    # remove data from DB
    db.execute("delete from {0} where guildid = {1} and channelid = {2}".format(table_name, channel.guild.id, channel.id))


async def getChannels(db: SqliteAccessor, table_name: str, guild: dc.Guild):
    # get channel-id from DB
    db.execute("select channelid from {0} where guildid = {1}".format(table_name, guild.id))
    # get channel objects and return
    ids = [i[0] for i in db.fetchall()]
    chs = await guild.fetch_channels()
    return [i for i in chs if i.id in ids]
