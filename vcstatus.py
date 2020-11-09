import discord as dc

intents = dc.Intents.default()

client = dc.Client(intents=intents)


@client.event
async def on_ready():
    print("Logged in as")
    print("User : ", client.user.name)
    print("ID   : ", client.user.id)
    print('------')


f = open("token.txt");
client.run(f.read())
