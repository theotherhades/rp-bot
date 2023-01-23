import os
#import pytz
import nextcord
#import threading
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from pymongo import MongoClient
from datetime import datetime

client = commands.Bot()

cluster = MongoClient(os.environ["DB_URL"])
db = cluster["test"]

GUILD_IDS = list()
for guild in client.guilds:
    GUILD_IDS.append(guild.id)

"""
def daily():
    threading.Timer(10, daily).start()

    now = datetime.now(pytz.utc)
    now = now.strftime("%H:%M:%S")

    if now == ""
"""

async def item_postpurchase(user, item: str, amount: int):
    """
    Do any extra tasks after an item has been purchased if needed, for example add troops to military balance (not just inv)
    """
    military_items = [
        "troops",
        "cavalry",
        "artillery",
        "boats",
        "aircraft"
    ]
    if item in military_items:
        newmil = db["users"].find_one({"_id": user.id})["military"]
        newmil[item] += amount
        db["users"].update_one({"_id": user.id}, {"$set": {"military": newmil}})

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
        button_military.disabled = False
        embed = nextcord.Embed(title = "General info", color = nextcord.Color.og_blurple())
        embed.set_author(name = data["name"].title(), icon_url = user.avatar.url)

        embed.add_field(name = "Treasury", value = f"${data['treasury']:,}", inline = False)
        embed.add_field(name = "Population", value = f"{data['population']:,}", inline = False)
        embed.add_field(name = "Stability", value = f"{data['stability']}", inline = False)

        await msg.edit(embed = embed, view = view)

    async def setpage_resources(interaction):
        nonlocal msg
        button_resources.disabled = True
        button_geninfo.disabled = False
        button_military.disabled = False
        embed = nextcord.Embed(title = "Resources")
        embed.set_author(name = data["name"].title(), icon_url = user.avatar.url)

        embed.add_field(name = "🪨 Steel", value = f"{data['resources']['steel']:,}", inline = False)
        embed.add_field(name = "🛢️ Oil", value = f"{data['resources']['oil']:,}", inline = False)
        embed.add_field(name = "🪵 Wood", value = f"{data['resources']['wood']:,}", inline = False)
        embed.add_field(name = "💎 Precious Metals", value = f"{data['resources']['precious_metals']:,}", inline = False)

        await msg.edit(embed = embed, view = view)

    async def setpage_military(interaction):
        nonlocal msg
        button_military.disabled = True
        button_geninfo.disabled = False
        button_resources.disabled = False
        embed = nextcord.Embed(title = "Military", color = nextcord.Color.brand_green())
        embed.set_author(name = data["name"].title(), icon_url = user.avatar.url)

        embed.add_field(name = "Troops", value = f"{data['military']['troops']:,}", inline = False)
        embed.add_field(name = "Cavalry", value = f"{data['military']['cavalry']:,}", inline = False)
        embed.add_field(name = "Artillery", value = f"{data['military']['artillery']:,}", inline = False)
        embed.add_field(name = "Boats", value = f"{data['military']['boats']:,}", inline = False)
        embed.add_field(name = "Aircraft", value = f"{data['military']['aircraft']:,}", inline = False)

        await msg.edit(embed = embed, view = view)

    embed = nextcord.Embed(title = "General info", color = nextcord.Color.og_blurple())
    embed.set_author(name = data["name"].title(), icon_url = user.avatar.url)

    embed.add_field(name = "Treasury", value = f"${data['treasury']:,}", inline = False)
    embed.add_field(name = "Population", value = f"{data['population']:,}", inline = False)
    embed.add_field(name = "Stability", value = f"{data['stability']}", inline = False)

    view = nextcord.ui.View(timeout = 180)

    # General info button
    button_geninfo = nextcord.ui.Button(emoji = "📔", style = nextcord.ButtonStyle.gray, disabled = True)
    button_geninfo.callback = setpage_geninfo
    view.add_item(button_geninfo)

    # Resources button
    button_resources = nextcord.ui.Button(emoji = "⛏️", style = nextcord.ButtonStyle.gray, disabled = False)
    button_resources.callback = setpage_resources
    view.add_item(button_resources)

    # Military button
    button_military = nextcord.ui.Button(emoji = "🪖", style = nextcord.ButtonStyle.gray, disabled = False)
    button_military.callback = setpage_military
    view.add_item(button_military)

    msg = await interaction.response.send_message(embed = embed, view = view)

@client.slash_command(name = "addmoney", description = "admin only", guild_ids = GUILD_IDS)
async def addmoney(interaction: Interaction, user: nextcord.User, amount: int):
    if interaction.user.id not in [
        655803366294683659, # Missourian
        687774746414546945 # me
    ]:
        await interaction.response.send_message(embed = nextcord.Embed(title = ":x: No perms?", description = "You don't have perms to do that!", color = nextcord.Color.red()), ephemeral = True)
    else:
        col = db["users"]
        data = col.find_one({"_id": user.id})
        col.update_one({"_id": user.id}, {"$set": {"treasury": data["treasury"] + amount}})
        await interaction.response.send_message(embed = nextcord.Embed(title = ":white_check_mark: Success!", description = f"Added **${amount:,}** to {data['name'].title()}'s balance.", color = nextcord.Color.green()), ephemeral = True)

@client.slash_command(name = "shop", description = "View shop items", guild_ids = GUILD_IDS)
async def shop(interaction: Interaction):
    col = db["shop"]
    shopitems = col.find_one({"_id": "shopitems"})
    embed = nextcord.Embed(title = "Shop", description = "You can purchase items with the `/buyitem` command.", color = nextcord.Color.blurple())
    for item in shopitems:
        if item != "_id":
            embed.add_field(name = item.title(), value = f"**Cost:** ${shopitems[item]['cost']}\n**Description:** {shopitems[item]['description']}")
    
    await interaction.response.send_message(embed = embed)

@client.slash_command(name = "buyitem", description = "Purchase an item from the shop", guild_ids = GUILD_IDS)
async def buyitem(interaction: Interaction, item = SlashOption(
    name = "item",
    choices = {
        k.title(): k for k in db["shop"].find_one({"_id": "shopitems"}) if k != "_id"
    }
), amount: int = 1):
    shopitems = db["shop"].find_one({"_id": "shopitems"})
    del shopitems["_id"]
    userdata = db["users"].find_one({"_id": interaction.user.id})

    if userdata["treasury"] >= shopitems[item]["cost"] * amount:
        newinv = userdata["inv"]
        if item not in newinv.keys():
            newinv[item] = amount
        else:
            newinv[item] += amount
        db["users"].update_one({"_id": interaction.user.id}, {"$set": {"treasury": userdata["treasury"] - shopitems[item]["cost"] * amount, "inv": newinv}})
        await item_postpurchase(interaction.user, item, amount)
        embed = nextcord.Embed(title = ":white_check_mark: Success!", description = f"You've purchased {amount:,} {item.title() + 's' if item.endswith('s') == False else item.title()} for **${(shopitems[item]['cost'] * amount):,}**. Your treasury now has **${db['users'].find_one({'_id': interaction.user.id})['treasury']:,}**.", color = nextcord.Color.green())
    else:
        embed = nextcord.Embed(title = ":x: Not enough money!", description = f"Your treasury doesn't have enough money to fulfil this purchase! You have **${userdata['treasury']:,}** but the purchase requires **${(shopitems[item]['cost'] * amount):,}**", color = nextcord.Color.red())

    await interaction.response.send_message(embed = embed)

# do something like this for money later https://stackoverflow.com/questions/63625246/discord-py-bot-run-function-at-specific-time-every-day

client.run(os.environ["CLIENT_TOKEN"])