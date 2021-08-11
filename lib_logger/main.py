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


def launch_logger(token: str, activeFlag: multiprocessing.Value = None):
    # set flag
    if not activeFlag == None:
        global activeProcessFlag
        global flagMP
        activeProcessFlag = activeFlag
        activeProcessFlag.value = pf.LAUNCHING
        flagMP = True
    
    client.run(token)
    
    # set flag
    if not activeFlag == None:
        activeProcessFlag.value = pf.INACTIVE


# main ---
if __name__ == "__main__":
    with open("../token.txt") as f:
        launch_logger(f.read())
