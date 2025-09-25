import discord

intents = discord.Intents.default()
intents.message_content = True
bot1 = commands.Bot(command_prefix="!", intents=intents)

async def start(token):
    await bot1.start(token)
