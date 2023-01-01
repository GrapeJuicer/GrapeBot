from settings import *
import sqlite3
import discord
from discord import app_commands
import sys
import signal

from lib import vote



def setup():
    connection = sqlite3.connect(DATABASE)
    vote.init(connection)
    return connection



connection: sqlite3.Connection = setup()
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client=client)



@tree.command(
    name='test',
    description='This is a test'
)
@app_commands.describe(
    message='Your message',
    hello='Hello message'
)
@app_commands.rename(
    message='text'
)
@app_commands.choices(
    hello=[
        app_commands.Choice(name='Good Morning', value='Good Morning'),
        app_commands.Choice(name='Good Afternoon', value='Good Afternoon'),
        app_commands.Choice(name='Good Evening', value='Good Evening'),
        app_commands.Choice(name='Good Night', value='Good Night')
    ]
)
@app_commands.guild_only
async def test(ctx: discord.Interaction, message: str, hello: str):
    await ctx.response.send_message('This is a test message.\nYour message is ...\n'+message+'\n'+hello)



@tree.command(
    name='vote',
    description='投票を行う'
)
@app_commands.describe(
    title='投票のお題',
    visible='投票結果を表示する際に投票先を表示する',
)
@app_commands.choices(
    visible=[
        app_commands.Choice(name='表示する', value='Yes'),
        app_commands.Choice(name='表示しない', value='No')
    ]
)
@app_commands.guild_only
async def vote_with_any_choices(ctx: discord.Interaction, title: str, visible: str='Yes'):
    try:
        await ctx.response.send_modal(vote.VoteModal(title=title, visible=visible))
    except Exception as e:
        print(e.with_traceback(sys.exc_info()[2]))


@client.event
async def on_ready():
    print('Bot is ready')
    await tree.sync()


def cleanup():
    global connection
    connection.close()


def signal_handler(signum, frame):
    cleanup()
    sys.exit(1)


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, signal_handler)
    try:
        with open(TOKEN) as f:
            client.run(f.read())
    finally:
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        cleanup()
