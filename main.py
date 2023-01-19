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

@client.slash_command(name = "join", description = "Join the game", guild_ids = GUILD_IDS)
async def join(interaction: Interaction, name: str = SlashOption(description = "The name of your nation. This can always be changed later.")):
    col = db["users"]
    if col.count_documents({"_id": interaction.user.id}, limit = 1) == 0:
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
        embed = nextcord.Embed(title = "Success!", description = f"You've successfully joined the game as **{name}**!", color = nextcord.Color.green())
    else:
        embed = nextcord.Embed(title = "Error", description = "You are already in the database!", color = nextcord.Color.red())

    await interaction.response.send_message(embed = embed)

@client.slash_command(name = "profile", description = "Get a user's profile. If none is specified it defaults to your profile.", guild_ids = GUILD_IDS)
async def profile(interaction: Interaction, user: nextcord.User = None):
    col = db["users"]
    if user == None:
        user = interaction.user
    data = col.find_one({"_id": user.id})

    async def setpage_geninfo(interaction):
        nonlocal msg
        button_geninfo.disabled = True
        button_resources.disabled = False
        embed = nextcord.Embed(title = "General info", color = nextcord.Color.og_blurple())
        embed.set_author(name = data["name"].title())

        embed.add_field(name = "Treasury", value = f"${data['treasury']}")
        embed.add_field(name = "Population", value = f"${data['population']}")
        embed.add_field(name = "Stability", value = f"${data['stability']}")

        await msg.edit(embed = embed, view = view)

    async def setpage_resources(interaction):
        nonlocal msg
        button_resources.disabled = True
        button_geninfo.disabled = False
        embed = nextcord.Embed(title = "Resources")
        embed.set_author(name = data["name"].title())

        await msg.edit(embed = embed, view = view)

    embed = nextcord.Embed(title = "General info", color = nextcord.Color.og_blurple())
    embed.set_author(name = data["name"].title())

    embed.add_field(name = "Treasury", value = f"${data['treasury']}")
    embed.add_field(name = "Population", value = f"{data['population']}")
    embed.add_field(name = "Stability", value = f"{data['stability']}")

    view = nextcord.ui.View(timeout = 180)

    # General info button
    button_geninfo = nextcord.ui.Button(emoji = "📔", style = nextcord.ButtonStyle.blurple, disabled = True)
    button_geninfo.callback = setpage_geninfo
    view.add_item(button_geninfo)

    # Resources button
    button_resources = nextcord.ui.Button(emoji = "⛏️", style = nextcord.ButtonStyle.blurple, disabled = False)
    button_resources.callback = setpage_resources
    view.add_item(button_resources)

    msg = await interaction.response.send_message(embed = embed, view = view)

@client.slash_command(name = "test_profile", description = "test", guild_ids = GUILD_IDS)
async def test_profile(interaction: Interaction):
    view = nextcord.ui.View(timeout = 180)
    button = nextcord.ui.Button(emoji = "📔", style = nextcord.ButtonStyle.blurple)
    view.add_item(button)
    embed = nextcord.Embed(title = "click the button", description = "do it")
    await interaction.response.send_message(embed = embed, view = view)

# do something like this for money later https://stackoverflow.com/questions/63625246/discord-py-bot-run-function-at-specific-time-every-day

client.run(os.environ["CLIENT_TOKEN"])