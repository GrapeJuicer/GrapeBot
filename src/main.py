import discord as dc
import vcstatus.vcstatus as vc

intents: dc.Intents = dc.Intents.default()
client: dc.Client = dc.Client(intents=intents)


# Botを呼び出すときのコマンド
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
    # メッセージの送信者が本Botだった場合は何もしない
    if message.author == client.user:
        return

    msgs = message.content.split(" ")

    if msgs[0] in gbauth:
        try:
            await message.channel.send("{0} is Not found. func test > {1}".format(msgs[1], vc.test()))
        except:
            # help に移行
            await message.channel.send("Invalid Usage.\nPlease enter '{0} help'".format(msgs[0]))


# main
f = open("../token.txt")
client.run(f.read())
