import discord

def get_intents():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.dm_messages = True
    intents.guilds = True
    return intents

bot2 = commands.Bot(command_prefix="!", intents=get_intents())

async def start(token):
    await bot1.start(token)
