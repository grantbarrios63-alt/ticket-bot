import os
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print("ERROR: DISCORD_TOKEN is not set in environment variables!")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

CATEGORY_NAME = "Tickets"
STAFF_ROLE_NAME = "Staff"


# ---------- TICKET CONTROLS ----------
class TicketControls(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Claim Ticket", style=discord.ButtonStyle.blurple)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):

        staff_role = discord.utils.get(interaction.guild.roles, name=STAFF_ROLE_NAME)

        if staff_role not in interaction.user.roles:
            await interaction.response.send_message(
                "Only staff can claim tickets.",
                ephemeral=True
            )
            return

        await interaction.channel.send(f"📌 Claimed by {interaction.user.mention}")
        await interaction.response.send_message("You claimed the ticket.", ephemeral=True)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):

        staff_role = discord.utils.get(interaction.guild.roles, name=STAFF_ROLE_NAME)

        if staff_role not in interaction.user.roles:
            await interaction.response.send_message(
                "Only staff can close tickets.",
                ephemeral=True
            )
            return

        await interaction.response.send_message("Closing ticket...", ephemeral=True)
        await interaction.channel.delete()


# ---------- BUTTON PANEL ----------
class TicketPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.green)
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild
        user = interaction.user

        category = discord.utils.get(guild.categories, name=CATEGORY_NAME)
        if category is None:
            category = await guild.create_category(CATEGORY_NAME)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }

        staff_role = discord.utils.get(guild.roles, name=STAFF_ROLE_NAME)
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True
            )

        channel = await guild.create_text_channel(
            name=f"ticket-{user.id}",
            category=category,
            overwrites=overwrites
        )

        await channel.send(
            content=f"{user.mention} Welcome! A staff member will help you soon.",
            view=TicketControls()
        )

        await interaction.response.send_message(
            f"Ticket created: {channel.mention}",
            ephemeral=True
        )


# ---------- COMMAND ----------
@bot.command()
async def panel(ctx):
    embed = discord.Embed(
        title="Support Tickets",
        description="Click the button below to create a ticket.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, view=TicketPanel())


# ---------- READY EVENT ----------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


# ---------- START BOT ----------
bot.run(TOKEN)
