import os
import nextcord
from nextcord import Interaction
from nextcord.ext import commands

client = commands.Bot()

GUILD_IDS = list()
for guild in client.guilds:
    GUILD_IDS.append(guild.id)

@client.extra_event
async def on_ready():
    print("Bot is online")

@client.slash_command(name = "hi", description = "says hi", guild_ids = GUILD_IDS)
async def hi(interaction: Interaction):
    interaction.response.send_message(f"hi {interaction.user.name}")

client.run(os.environ["CLIENT_TOKEN"])