import discord as dc
import vcstatus.vcstatus as vc

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
            # print("error !")
            await sendErr(msgs, message.channel)


# message processing
async def messageProcess(messages: list, channel: dc.TextChannel):
    if (messages[1] == "test"):  # test -------------------------
        await channel.send(vc.test())
    else:
        # print("non match !")
        raise Exception("NonMatchError")


# send error message to discord
async def sendErr(messages: list, channel: dc.TextChannel):
    str = "Invalid Usage.\n"
    str += "'" + " ".join(messages) + "' is not exist.\n"
    str += "Please enter '{0} help'.".format(messages[0])
    await channel.send(str)


# main
f = open("token.txt")
client.run(f.read())
