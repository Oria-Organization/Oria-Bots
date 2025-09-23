import asyncio
from oria_communauté.bot1.py import bot1.py
from nexara_officiel.bot2.py import bot2.py

#Lancement des bots
async def main():
    await asyncio.gather(
        bot1.start("TOKEN_BOT1"),
        bot2.start("TOKEN_BOT2"))
asyncio.run(main())
