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

bot2 = commands.Bot(command_prefix="!", intents=get_intents())

def is_admin(user: discord.User | discord.Member) -> bool:
    return user.id in ADMIN_IDS

@bot2.event
async def on_ready():
    await bot2.tree.sync()
    print(f"✅ Bot2 connecté en tant que {bot2.user}")
    channel_id = 1408354449172463686
    try:
        channel = bot2.get_channel(channel_id)
        if channel:
            await channel.send(f"🚀 Bot2 est démarré et prêt ! (User: {bot2.user})")
        else:
            print(f"❌ Salon {channel_id} introuvable (peut-être pas dans les intents/guilds ?)")
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi du message de démarrage : {e}")

# --- /mp : Envoie un MP à un utilisateur ---
@bot2.tree.command(name="mp", description="Envoyer un MP à un utilisateur")
@app_commands.describe(user_id="ID de l'utilisateur", message="Message à envoyer")
async def mp(interaction: discord.Interaction, user_id: str, message: str):
    if not is_admin(interaction.user):
        return await interaction.response.send_message("⛔ Accès refusé.", ephemeral=True)
    try:
        user = await bot2.fetch_user(int(user_id))
        await user.send(message)
        await interaction.response.send_message("✅ MP envoyé !", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"⛔ Erreur : {e}", ephemeral=True)

# --- /embed : Formulaire interactif pour créer un embed ---
class EmbedModal(discord.ui.Modal, title="Créer un embed"):
    titre = discord.ui.TextInput(label="Titre", style=discord.TextStyle.short)
    description = discord.ui.TextInput(label="Description", style=discord.TextStyle.paragraph)
    couleur = discord.ui.TextInput(label="Couleur hex (ex : #00aaff)", style=discord.TextStyle.short, required=False)
    image = discord.ui.TextInput(label="URL de l'image", style=discord.TextStyle.short, required=False)

    def __init__(self, channel: discord.abc.Messageable):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        color = discord.Color.default()
        if self.couleur.value:
            try:
                color = discord.Color.from_str(self.couleur.value)
            except:
                pass
        embed = discord.Embed(title=self.titre.value, description=self.description.value, color=color)
        if self.image.value:
            embed.set_image(url=self.image.value)
        await self.channel.send(embed=embed)
        await interaction.response.send_message("✅ Embed envoyé !", ephemeral=True)

@bot2.tree.command(name="embed", description="Créer un embed personnalisé")
@app_commands.describe(channel="Salon de destination")
async def embed(interaction: discord.Interaction, channel: discord.TextChannel):
    if not is_admin(interaction.user):
        return await interaction.response.send_message("⛔ Accès refusé.", ephemeral=True)
    await interaction.response.send_modal(EmbedModal(channel))

# --- /envoyer : Envoie un message classique ---
class EnvoyerModal(discord.ui.Modal, title="Envoyer un message"):
    contenu = discord.ui.TextInput(label="Contenu du message", style=discord.TextStyle.paragraph)
    def __init__(self, channel: discord.abc.Messageable):
        super().__init__()
        self.channel = channel
    async def on_submit(self, interaction: discord.Interaction):
        await self.channel.send(self.contenu.value)
        await interaction.response.send_message("✅ Message envoyé !", ephemeral=True)

@bot2.tree.command(name="envoyer", description="Envoyer un message classique dans un salon")
@app_commands.describe(channel="Salon de destination")
async def envoyer(interaction: discord.Interaction, channel: discord.TextChannel):
    if not is_admin(interaction.user):
        return await interaction.response.send_message("⛔ Accès refusé.", ephemeral=True)
    await interaction.response.send_modal(EnvoyerModal(channel))

# --- /modifier_message : Modifie un message du bot ---
@bot2.tree.command(name="modifier_message", description="Modifier un message envoyé par le bot")
@app_commands.describe(message_id="ID du message à modifier", new_content="Nouveau contenu")
async def modifier_message(interaction: discord.Interaction, message_id: str, new_content: str):
    if not is_admin(interaction.user):
        return await interaction.response.send_message("⛔ Accès refusé.", ephemeral=True)
    try:
        for channel in interaction.guild.text_channels:
            try:
                msg = await channel.fetch_message(int(message_id))
                if msg.author.id == bot2.user.id:
                    await msg.edit(content=new_content)
                    return await interaction.response.send_message("✅ Message modifié !", ephemeral=True)
            except:
                continue
        await interaction.response.send_message("⛔ Message introuvable ou non envoyé par le bot.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"⛔ Erreur : {e}", ephemeral=True)

# --- /modifier_embed : Modifier un embed via formulaire ---
class ModifierEmbedModal(discord.ui.Modal, title="Modifier un embed"):
    titre = discord.ui.TextInput(label="Titre", style=discord.TextStyle.short)
    description = discord.ui.TextInput(label="Description", style=discord.TextStyle.paragraph)
    couleur = discord.ui.TextInput(label="Couleur hex (ex : #00aaff)", style=discord.TextStyle.short, required=False)
    image = discord.ui.TextInput(label="URL de l'image", style=discord.TextStyle.short, required=False)
    def __init__(self, message: discord.Message):
        super().__init__()
        self.message = message
        if message.embeds:
            emb = message.embeds[0]
            self.titre.default = emb.title or ""
            self.description.default = emb.description or ""
            if emb.color:
                self.couleur.default = f"#{emb.color.value:06x}"
            if emb.image:
                self.image.default = emb.image.url or ""
    async def on_submit(self, interaction: discord.Interaction):
        color = discord.Color.default()
        if self.couleur.value:
            try:
                color = discord.Color.from_str(self.couleur.value)
            except:
                pass
        embed = discord.Embed(title=self.titre.value, description=self.description.value, color=color)
        if self.image.value:
            embed.set_image(url=self.image.value)
        await self.message.edit(embed=embed)
        await interaction.response.send_message("✅ Embed modifié !", ephemeral=True)

@bot2.tree.command(name="modifier_embed", description="Modifier un embed publié")
@app_commands.describe(message_id="ID du message à modifier")
async def modifier_embed(interaction: discord.Interaction, message_id: str):
    if not is_admin(interaction.user):
        return await interaction.response.send_message("⛔ Accès refusé.", ephemeral=True)
    try:
        for channel in interaction.guild.text_channels:
            try:
                msg = await channel.fetch_message(int(message_id))
                if msg.author.id == bot2.user.id and msg.embeds:
                    return await interaction.response.send_modal(ModifierEmbedModal(msg))
            except:
                continue
        await interaction.response.send_message("⛔ Message/embed introuvable ou non envoyé par le bot.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"⛔ Erreur : {e}", ephemeral=True)

# --- /blacklist ---
# Remplace la logique par ta vraie gestion, ici c'est un exemple en mémoire
blacklist_db = {"staff": {}, "serveur": {}}

@bot2.tree.command(name="blacklist", description="Blacklist un utilisateur")
@app_commands.describe(user_id="ID de l'utilisateur",
                       categorie="Catégorie (staff ou serveur)",
                       raison="Raison")
async def blacklist(interaction: discord.Interaction, user_id: str, categorie: str, raison: str):
    if not is_admin(interaction.user):
        return await interaction.response.send_message("⛔ Accès refusé.", ephemeral=True)
    if categorie not in blacklist_db:
        return await interaction.response.send_message("⛔ Catégorie inconnue.", ephemeral=True)
    blacklist_db[categorie][user_id] = {"raison": raison, "date": discord.utils.utcnow().isoformat()}
    await interaction.response.send_message(f"✅ Utilisateur {user_id} blacklisté en {categorie} pour : {raison}", ephemeral=True)

@bot2.tree.command(name="list-blacklist", description="Liste des blacklistés")
@app_commands.describe(categorie="Catégorie (staff ou serveur)")
async def list_blacklist(interaction: discord.Interaction, categorie: str):
    if not is_admin(interaction.user):
        return await interaction.response.send_message("⛔ Accès refusé.", ephemeral=True)
    if categorie not in blacklist_db:
        return await interaction.response.send_message("⛔ Catégorie inconnue.", ephemeral=True)
    entries = blacklist_db[categorie]
    if not entries:
        return await interaction.response.send_message("Aucun utilisateur blacklisté dans cette catégorie.", ephemeral=True)
    txt = "**Blacklist :**\n"
    for uid, data in entries.items():
        txt += f"- {uid} → {data['raison']} ({data['date']})\n"
    await interaction.response.send_message(txt, ephemeral=True)
