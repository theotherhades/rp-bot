import os
import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from pymongo import MongoClient

client = commands.Bot()

cluster = MongoClient(os.environ["DB_URL"])
db = cluster["test"]

GUILD_IDS = list()
for guild in client.guilds:
    GUILD_IDS.append(guild.id)

@client.event
async def on_ready():
    print("Bot is online")

@client.slash_command(name = "hi", description = "says hi", guild_ids = GUILD_IDS)
async def hi(interaction: Interaction):
    await interaction.response.send_message(f"hi {interaction.user.name}")

@client.slash_command(name = "join", description = "", guild_ids = GUILD_IDS)
async def join(interaction: Interaction, name: str = SlashOption(description = "The name of your nation. This can always be changed later.")):
    col = db["users"]
    col.insert_one({
        "_id": interaction.user.id,
        "name": name,
        "treasury": 100000,
        "population": 1000,
        "stability": 10,
        "resources": {
            "steel": 0,
            "oil": 0,
            "wood": 0,
            "precious_metals": 0
        },
        "military": {
            "troops": 0,
            "cavalry": 0,
            "artillery": 0,
            "boats": 0,
            "aircraft": 0
        }
    })
    embed = nextcord.Embed(title = "Success!", description = f"You've successfully joined the game as **{name}**!")
    await interaction.response.send_message(embed = embed)

# do something like this for money later https://stackoverflow.com/questions/63625246/discord-py-bot-run-function-at-specific-time-every-day

client.run(os.environ["CLIENT_TOKEN"])