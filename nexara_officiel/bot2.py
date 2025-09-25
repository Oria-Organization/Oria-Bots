import discord
from discord import app_commands
from discord.ext import commands

async def start(token):
    await bot2.start(token)

ADMIN_IDS = {1209546018639843331, 1366117716863357060, 1390717909386530876}

# --- Intents ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.dm_messages = True
intents.guilds = True

# --- Bot setup ---
bot = commands.Bot(command_prefix="!", intents=intents)

# --- Vérifie si l'utilisateur est admin ---
def is_admin(user: discord.User | discord.Member):
    return user.id in ADMIN_IDS

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot1 connecté en tant que {bot.user}")

# --- Modal pour envoyer un message ---
class EnvoyerModal(discord.ui.Modal, title="Envoyer un message"):
    contenu = discord.ui.TextInput(label="Contenu du message", style=discord.TextStyle.paragraph)

    def __init__(self, channel: discord.abc.Messageable):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        await self.channel.send(self.contenu.value)
        await interaction.response.send_message("✅ Message envoyé avec succès.", ephemeral=True)

@bot.tree.command(name="envoyer", description="Envoyer un message dans un salon ou un fil")
@app_commands.describe(channel="Salon ou fil de destination")
async def envoyer(interaction: discord.Interaction, channel: discord.abc.GuildChannel):
    if not is_admin(interaction.user):
        return await interaction.response.send_message("⛔ Accès refusé.", ephemeral=True)
    await interaction.response.send_modal(EnvoyerModal(channel))

# --- Modal pour créer un embed ---
class EmbedModal(discord.ui.Modal, title="Créer un embed"):
    titre = discord.ui.TextInput(label="Titre", style=discord.TextStyle.short, required=True)
    description = discord.ui.TextInput(label="Description", style=discord.TextStyle.paragraph, required=True)

    def __init__(self, channel: discord.abc.Messageable):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        emb = discord.Embed(title=self.titre.value, description=self.description.value, color=0x00aaff)
        await self.channel.send(embed=emb)
        await interaction.response.send_message("✅ Embed envoyé avec succès.", ephemeral=True)

@bot.tree.command(name="embed", description="Créer un embed dans un salon ou un fil")
@app_commands.describe(channel="Salon ou fil de destination")
async def embed(interaction: discord.Interaction, channel: discord.abc.GuildChannel):
    if not is_admin(interaction.user):
        return await interaction.response.send_message("⛔ Accès refusé.", ephemeral=True)
    await interaction.response.send_modal(EmbedModal(channel))

# --- Commande /mp ---
@bot.tree.command(name="mp", description="Envoyer un message privé à un utilisateur")
@app_commands.describe(user_id="ID de l'utilisateur")
async def mp(interaction: discord.Interaction, user_id: str):
    if not is_admin(interaction.user):
        return await interaction.response.send_message("⛔ Accès refusé.", ephemeral=True)
    try:
        target_user = await bot.fetch_user(int(user_id))

        class MpModal(discord.ui.Modal, title="Envoyer un MP"):
            contenu = discord.ui.TextInput(label="Contenu du message", style=discord.TextStyle.paragraph)
            async def on_submit(self, modal_inter: discord.Interaction):
                await target_user.send(self.contenu.value)
                await modal_inter.response.send_message("✅ MP envoyé avec succès.", ephemeral=True)

        await interaction.response.send_modal(MpModal())
    except Exception as e:
        await interaction.response.send_message(f"⛔ Erreur : {e}", ephemeral=True)

# --- Modal pour modifier un message existant (texte + embed) ---
class ModifierModal(discord.ui.Modal, title="Modifier un message"):
    contenu = discord.ui.TextInput(label="Nouveau contenu texte", style=discord.TextStyle.paragraph, required=False)
    titre_embed = discord.ui.TextInput(label="Titre de l'embed", style=discord.TextStyle.short, required=False)
    description_embed = discord.ui.TextInput(label="Description de l'embed", style=discord.TextStyle.paragraph, required=False)
    couleur_embed = discord.ui.TextInput(label="Couleur de l'embed (hex, ex: #ff0000)", style=discord.TextStyle.short, required=False)

    def __init__(self, message: discord.Message):
        super().__init__()
        self.message = message

        # Préremplir avec l’existant
        self.contenu.default = message.content if message.content else ""
        if message.embeds:
            embed = message.embeds[0]
            self.titre_embed.default = embed.title or ""
            self.description_embed.default = embed.description or ""
            if embed.color:
                self.couleur_embed.default = f"#{embed.color.value:06x}"

    async def on_submit(self, interaction: discord.Interaction):
        try:
            new_content = self.contenu.value

            # Reconstruire l’embed uniquement si un champ est rempli
            embed = None
            if self.titre_embed.value or self.description_embed.value or self.couleur_embed.value:
                embed = discord.Embed(
                    title=self.titre_embed.value or None,
                    description=self.description_embed.value or None,
                    color=discord.Color.from_str(self.couleur_embed.value) if self.couleur_embed.value else discord.Color.default()
                )

            await self.message.edit(content=new_content, embed=embed)
            await interaction.response.send_message("✅ Message modifié avec succès.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"⛔ Erreur : {e}", ephemeral=True)

@bot.tree.command(name="modifier", description="Modifier un message déjà envoyé par le bot")
@app_commands.describe(message_id="ID du message à modifier")
async def modifier(interaction: discord.Interaction, message_id: str):
    if not is_admin(interaction.user):
        return await interaction.response.send_message("⛔ Accès refusé.", ephemeral=True)
    try:
        for channel in interaction.guild.text_channels:
            try:
                msg = await channel.fetch_message(int(message_id))
                if msg.author.id == bot.user.id:
                    return await interaction.response.send_modal(ModifierModal(msg))
            except:
                continue
        await interaction.response.send_message("⛔ Message introuvable ou non envoyé par moi.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"⛔ Erreur : {e}", ephemeral=True)
