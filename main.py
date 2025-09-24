import asyncio
import os
from dotenv import load_dotenv
from oria_communauté.bot1 import bot1
from nexara_officiel.bot2 import bot2
import discord

intents = discord.Intents.default()
intents.message_content = True
load_dotenv()

async def main():
    token1 = os.getenv("TOKEN_BOT1")
    token2 = os.getenv("TOKEN_BOT2")
    await asyncio.gather(
        bot1.start(token1),
        bot2.start(token2)
    )

asyncio.run(main())
