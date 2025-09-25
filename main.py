import asyncio
import os
from oria_communauté.bot1 import bot1
from nexara_officiel.bot2 import bot2
import discord

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def get_intents():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.dm_messages = True
    intents.guilds = True
    return intents

async def run_bot(bot, token, name):
    if not token:
        print(f"❌ Token manquant pour {name}. Vérifie la configuration de ton hébergeur ou le .env")
        return
    try:
        await bot.start(token)
    except Exception as e:
        print(f"❌ {name} n'a pas pu démarrer: {e}")

async def main():
    token1 = os.getenv("TOKEN_BOT1")
    token2 = os.getenv("TOKEN_BOT2")

    bot1.intents = get_intents()
    bot2.intents = get_intents()

    await asyncio.gather(
        run_bot(bot1, token1, "Bot1"),
        run_bot(bot2, token2, "Bot2")
    )

if __name__ == "__main__":
    asyncio.run(main())
