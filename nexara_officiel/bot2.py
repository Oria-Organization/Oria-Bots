import discord

intents = discord.Intents.default()
intents.message_content = True
bot2 = discord.Client(intents=intents)

async def start(token):
    await bot2.start(token)
