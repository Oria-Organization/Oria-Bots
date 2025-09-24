import discord

intents = discord.Intents.default()
intents.message_content = True
bot1 = discord.Client()

async def start(token):
    await bot1.start(token)
