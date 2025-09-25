import discord
from discord import app_commands
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot2 = commands.Bot(command_prefix="!", intents=intents)

async def start(token):
    await bot2.start(token)

# Modal du MP
class MPModal(discord.ui.Modal, title="Envoyer un MP"):
    message = discord.ui.TextInput(label="Message", style=discord.TextStyle.paragraph)

    def __init__(self, recipient: discord.User):
        super().__init__()
        self.recipient = recipient

    async def on_submit(self, interaction: discord.Interaction):
        reply_button = ReplyButton(sender_id=interaction.user.id)
        try:
            await self.recipient.send(
                f"**Nouveau MP de {interaction.user.mention} :**\n{self.message.value}",
                view=reply_button
            )
            await interaction.response.send_message("Message envoyé !", ephemeral=True)
        except Exception:
            await interaction.response.send_message("Impossible d'envoyer le MP (l'utilisateur n'accepte peut-être pas les MP).", ephemeral=True)

# Renvoie d'un MP
class ReplyModal(discord.ui.Modal, title="Répondre au MP"):
    message = discord.ui.TextInput(label="Votre réponse", style=discord.TextStyle.paragraph)

    def __init__(self, recipient: discord.User):
        super().__init__()
        self.recipient = recipient

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await self.recipient.send(f"**Réponse à votre MP :**\n{self.message.value}")
            await interaction.response.send_message("Réponse envoyée !", ephemeral=True)
        except Exception:
            await interaction.response.send_message("Impossible d'envoyer la réponse.", ephemeral=True)

class ReplyButton(discord.ui.View):
    def __init__(self, sender_id: int):
        super().__init__(timeout=None)
        self.sender_id = sender_id

    @discord.ui.button(label="Répondre", style=discord.ButtonStyle.primary)
    async def reply(self, interaction: discord.Interaction, button: discord.ui.Button):
        sender = await interaction.client.fetch_user(self.sender_id)
        await interaction.response.send_modal(ReplyModal(recipient=sender))

class MP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

# Commande MP
    @app_commands.command(name="mp", description="Envoyer un message privé à un utilisateur via son ID")
    @app_commands.describe(user_id="ID de l'utilisateur à contacter")
    async def mp(self, interaction: discord.Interaction, user_id: str):
        try:
            user = await self.bot.fetch_user(int(user_id))
            await interaction.response.send_modal(MPModal(recipient=user))
        except Exception:
            await interaction.response.send_message("Utilisateur introuvable.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(MP(bot))
