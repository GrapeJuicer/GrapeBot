"""
include packages
"""

from settings import *
import sqlite3
import discord
from discord import app_commands
import sys
import signal
import deepl
from typing import Optional

from lib import vote as vt
from lib import deepl as dl



"""
Global variables
"""

connection : sqlite3.Connection       = sqlite3.connect(DATABASE)
intents    : discord.Intents          = discord.Intents.all()
client     : discord.Client           = discord.Client(intents=intents)
tree       : app_commands.CommandTree = app_commands.CommandTree(client=client)



"""
Setup
"""

vt.init(connection)
with open(DEEPL_API_KEY) as f:
    dl_translator = dl.LoggingTranslator(f.read(), connection=connection)



"""
Commands
"""

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
        await ctx.response.send_modal(vt.VoteModal(title=title, visible=visible))
    except Exception as e:
        print(e.with_traceback(sys.exc_info()[2]))



@tree.command(
    name='deepl',
    description='DeepL翻訳を使用してテキストを翻訳する（default: Auto→JP）'
)
@app_commands.describe(
    text='翻訳するテキスト',
    source_language='翻訳前の言語（default: 自動検出）',
    target_language='翻訳後の言語（default: 日本語）'
)
@app_commands.choices(
    source_language=dl.DcLanguageList.SOURCE,
    target_language=dl.DcLanguageList.TARGET
)
async def deepl_translate(ctx: discord.Interaction, text: str, source_language: Optional[str] = None, target_language: str = deepl.Language.JAPANESE):
    try:
        if source_language == "":
            source_language = None

        translated_text = dl_translator.translate_text(
            ctx=ctx,
            text=text,
            source_lang=source_language,
            target_lang=target_language
        )

        t = "> " + text.replace("\n", "\n> ") + "\n"

        await ctx.response.send_message(t + translated_text.text)

    except Exception as e:
        print(e.with_traceback(sys.exc_info()[2]))



"""
Events
"""

@client.event
async def on_ready():
    print('Bot is ready')
    await tree.sync()



"""
Cleanups
"""

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
