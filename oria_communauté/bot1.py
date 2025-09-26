import discord
from discord import app_commands
from discord.ext import commands

ADMIN_IDS = {1209546018639843331, 1366117716863357060, 1390717909386530876}

def get_intents():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.dm_messages = True
    intents.guilds = True
    return intents

bot1 = commands.Bot(command_prefix="!", intents=get_intents())

def is_admin(user: discord.User | discord.Member) -> bool:
    return user.id in ADMIN_IDS

@bot1.event
async def on_ready():
    await bot1.tree.sync()
    print(f"✅ Bot1 connecté en tant que {bot1.user}")

    # Envoi du message de démarrage dans le salon Discord
    channel_id = 1408354449172463686
    try:
        channel = bot1.get_channel(channel_id)
        if channel:
            await channel.send(f"🚀 Bot1 est démarré et prêt ! (User: {bot1.user})")
        else:
            print(f"❌ Salon {channel_id} introuvable (peut-être pas dans les intents/guilds ?)")
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi du message de démarrage : {e}")

# ---- Commandes slash ----

@bot1.tree.command(name="info-serveur", description="Affiche les infos du serveur")
async def info_serveur(interaction: discord.Interaction):
    guild = interaction.guild
    if guild is None:
        return await interaction.response.send_message("⛔ Commande à utiliser dans un serveur.", ephemeral=True)
    n_membres = guild.member_count
    creation = guild.created_at.strftime("%d/%m/%Y %H:%M")
    salons = len(guild.channels)
    connectés = sum(1 for m in guild.members if m.status != discord.Status.offline)
    txt = (f"**Infos du serveur :**\n"
           f"- Membres : {n_membres}\n"
           f"- Date création : {creation}\n"
           f"- Membres connectés : {connectés}\n"
           f"- Salons : {salons}")
    await interaction.response.send_message(txt, ephemeral=True)

@bot1.tree.command(name="info-utilisateur", description="Infos sur un utilisateur")
@app_commands.describe(user="Utilisateur à inspecter")
async def info_utilisateur(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    txt = (f"**Infos sur {user.mention}**\n"
           f"ID : {user.id}\n"
           f"Arrivé : {user.joined_at.strftime('%d/%m/%Y %H:%M') if user.joined_at else 'N/A'}\n"
           f"Rôles : {', '.join([r.mention for r in user.roles if r != interaction.guild.default_role])}")
    # Blacklist check (exemple, à adapter selon système réel)
    if hasattr(user, 'blacklisted') and user.blacklisted:
        txt += f"\n⚠️ Blacklisté par le staff : {user.blacklist_reason}"
    await interaction.response.send_message(txt, ephemeral=True)

@bot1.tree.command(name="info-wiki", description="Informations sur le wiki du serveur")
async def info_wiki(interaction: discord.Interaction):
    await interaction.response.send_message("🔗 Wiki du serveur : https://lien-du-wiki.fr", ephemeral=True)

@bot1.tree.command(name="pseudo", description="Change le pseudo d'un membre, d'un rôle ou tout le serveur")
@app_commands.describe(
    membre="Le membre à cibler (optionnel)",
    role="Le rôle à cibler (optionnel)",
    everyone="Changer pour tout le serveur ? (optionnel)",
    nouveau_nom="Nouveau pseudo (utilisez $1 pour le pseudo d'origine)"
)
async def pseudo(
    interaction: discord.Interaction,
    nouveau_nom: str,
    membre: discord.Member = None,
    role: discord.Role = None,
    everyone: bool = False
):
    if not is_admin(interaction.user):
        return await interaction.response.send_message("⛔ Accès réservé au staff.", ephemeral=True)

    guild = interaction.guild
    changed = 0
    if membre:
        base = membre.display_name
        new_name = nouveau_nom.replace("$1", base)
        await membre.edit(nick=new_name)
        changed += 1
    elif role:
        for member in role.members:
            base = member.display_name
            new_name = nouveau_nom.replace("$1", base)
            try:
                await member.edit(nick=new_name)
                changed += 1
            except: continue
    elif everyone:
        for member in guild.members:
            if member.bot: continue
            base = member.display_name
            new_name = nouveau_nom.replace("$1", base)
            try:
                await member.edit(nick=new_name)
                changed += 1
            except: continue
    else:
        return await interaction.response.send_message("⛔ Précise la cible (membre, rôle ou everyone).", ephemeral=True)
    await interaction.response.send_message(f"✅ Pseudos changés : {changed}", ephemeral=True)
