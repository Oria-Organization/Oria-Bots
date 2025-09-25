import discord

def get_intents():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.dm_messages = True
    intents.guilds = True
    return intents

bot2 = commands.Bot(command_prefix="!", intents=get_intents())

def is_admin(user: discord.User | discord.Member) -> bool:
    return user.id in ADMIN_IDS

@bot2.event
async def on_ready():
    await bot2.tree.sync()
    print(f"✅ Bot2 connecté en tant que {bot2.user}")

    # Envoi du message de démarrage dans le salon Discord
    channel_id = 1408354449172463686  # Remplace par l'ID de ton salon
    try:
        channel = bot2.get_channel(channel_id)
        if channel:
            await channel.send(f"🚀 Bot2 est démarré et prêt ! (User: {bot2.user})")
        else:
            print(f"❌ Salon {channel_id} introuvable (peut-être pas dans les intents/guilds ?)")
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi du message de démarrage : {e}")
