import tokens
import time
import asyncio
import random
import nextcord
import datetime
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from pymongo import MongoClient

client = commands.Bot()

cluster = MongoClient(tokens.db_url)
db = cluster["test"]

GUILD_IDS = list()
for guild in client.guilds:
    GUILD_IDS.append(guild.id)

async def logmsg(msg: str, function: str):
    """
    Logs msg to #bot-testing
    """
    channel = client.get_channel(1066223000183132181)
    await channel.send(f"{msg}\n> :notepad_spiral: Log from function `{function}`\n--------------------")

async def item_postpurchase(user, item: str, amount: int):
    """
    Do any extra tasks after an item has been purchased if needed, for example add troops to military balance (not just inv)
    """
    military_items = [
        "troops",
        "tanks",
        "artillery",
        "frigates",
        "destroyers",
        "cruisers",
        "submarines",
        "aircraft_carriers",
        "fighter_aircraft",
        "bomber_aircraft",
        "attack_aircraft"
    ]
    if item in military_items:
        newmil = db["users"].find_one({"_id": user.id})["military"]
        newmil[item] += amount
        db["users"].update_one({"_id": user.id}, {"$set": {"military": newmil}})

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
            "military": {"troops": 0, "tanks": 0, "artillery": 0, "frigates": 0, "destroyers": 0, "cruisers": 0, "submarines": 0, "aircraft_carriers": 0, "fighter_aircraft": 0, "bomber_aircraft": 0, "attack_aircraft": 0}
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
        button_research.disabled = False
        embed = nextcord.Embed(title = "General info", color = nextcord.Color.og_blurple())
        embed.set_author(name = data["name"].title(), icon_url = user.avatar.url)

        embed.add_field(name = "Treasury", value = f"${data['treasury']:,}", inline = False)
        embed.add_field(name = "Population", value = f"{data['population']:,}", inline = False)
        embed.add_field(name = "Stability", value = f"{data['stability']}", inline = False)

        await msg.edit(embed = embed, view = view)
        await logmsg(f"Updated page in profile embed to general\nProfile ID: `{user.id}`", "profile.setpage_geninfo")

    async def setpage_resources(interaction):
        nonlocal msg
        button_resources.disabled = True
        button_geninfo.disabled = False
        button_military.disabled = False
        button_research.disabled = False
        embed = nextcord.Embed(title = "Resources")
        embed.set_author(name = data["name"].title(), icon_url = user.avatar.url)

        embed.add_field(name = "🪨 Steel", value = f"{data['resources']['steel']:,}", inline = False)
        embed.add_field(name = "🛢️ Oil", value = f"{data['resources']['oil']:,}", inline = False)
        embed.add_field(name = "🪵 Wood", value = f"{data['resources']['wood']:,}", inline = False)
        embed.add_field(name = "💎 Precious Metals", value = f"{data['resources']['precious_metals']:,}", inline = False)

        await msg.edit(embed = embed, view = view)
        await logmsg(f"Updated page in profile embed to resources\nProfile ID: `{user.id}`", "profile.setpage_resources")

    async def setpage_military(interaction):
        nonlocal msg
        button_military.disabled = True
        button_geninfo.disabled = False
        button_resources.disabled = False
        button_research.disabled = False
        embed = nextcord.Embed(title = "Military", color = nextcord.Color.brand_green())
        embed.set_author(name = data["name"].title(), icon_url = user.avatar.url)

        """
        embed.add_field(name = "Troops", value = f"{data['military']['troops']:,}", inline = False)
        embed.add_field(name = "Tanks", value = f"{data['military']['tanks']:,}", inline = False)
        embed.add_field(name = "Artillery", value = f"{data['military']['artillery']:,}", inline = False)
        embed.add_field(name = "⚓ Frigates", value = f"{data['military']['frigates']:,}", inline = True)
        embed.add_field(name = "⚓ Destroyers", value = f"{data['military']['destroyers']:,}", inline = False)
        embed.add_field(name = "⚓ Cruisers", value = f"{data['military']['cruisers']:,}", inline = False)
        embed.add_field(name = "⚓ Submarines", value = f"{data['military']['submarines']:,}", inline = False)
        embed.add_field(name = "🛩️ Fighters", value = f"{data['military']['fighter_aircraft']:,}", inline = True)
        embed.add_field(name = "🛩️ Bombers", value = f"{data['military']['bomber_aircraft']:,}", inline = False)
        embed.add_field(name = "🛩️ Attack Aircraft", value = f"{data['military']['attack_aircraft']:,}", inline = False)
        """
        # Add one field each for army, navy and air force instead of one field per military unit
        embed.add_field(name = "🪖 Army", value = f"Troops: {data['military']['troops']:,}\nTanks: {data['military']['tanks']:,}\nArtillery: {data['military']['artillery']:,}", inline = False)
        embed.add_field(name = "⚓ Navy", value = f"Frigates: {data['military']['frigates']:,}\nDestroyers: {data['military']['destroyers']:,}\nCruisers: {data['military']['cruisers']:,}\nSubmarines: {data['military']['submarines']:,}\nAircraft Carriers: {data['military']['aircraft_carriers']:,}", inline = False)
        embed.add_field(name = "🛩️ Air Force", value = f"Fighters: {data['military']['fighter_aircraft']:,}\nBombers: {data['military']['bomber_aircraft']:,}\nAttack Aircraft: {data['military']['attack_aircraft']:,}", inline = False)

        await msg.edit(embed = embed, view = view)
        await logmsg(f"Updated page in profile embed to military\nProfile ID: `{user.id}`", "profile.setpage_military")

    async def setpage_research(interaction):
        nonlocal msg
        button_military.disabled = False
        button_geninfo.disabled = False
        button_resources.disabled = False
        button_research.disabled = True
        embed = nextcord.Embed(title = "Research", description = f"Research points: {data['research_points']}", color = nextcord.Color.purple())
        embed.set_author(name = data["name"].title(), icon_url = user.avatar.url)

        embed.add_field(name = "⛏️ Mining", value = f"Points: {data['research']['mining']}", inline = False)
        embed.add_field(name = "🛢️ Oil Refinery", value = f"Points: {data['research']['oil_refinery']}", inline = False)
        embed.add_field(name = "🪨 Steel Refinery", value = f"Points: {data['research']['steel_refinery']}", inline = False)
        embed.add_field(name = "🌲 Forestry", value = f"Points: {data['research']['forestry']}", inline = False)
        embed.add_field(name = "✨ Development", value = f"Points: {data['research']['development']}", inline = False)
        embed.set_footer(text = "Use `/research` to use your research points.")

        await msg.edit(embed = embed, view = view)
        await logmsg(f"Updated page in profile embed to research\nProfile ID: `{user.id}`", "profile.setpage_research")

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

    # Research button
    button_research = nextcord.ui.Button(emoji = "🧪", style = nextcord.ButtonStyle.gray, disabled = False)
    button_research.callback = setpage_research
    view.add_item(button_research)

    # Military button
    button_military = nextcord.ui.Button(emoji = "🪖", style = nextcord.ButtonStyle.gray, disabled = False)
    button_military.callback = setpage_military
    view.add_item(button_military)

    msg = await interaction.response.send_message(embed = embed, view = view)
    await logmsg(f"Created profile embed\nProfile ID: `{user.id}`", "profile")

@client.slash_command(name = "lb", description = "View a leaderboard of all nations.", guild_ids = GUILD_IDS)
async def lb(interaction: Interaction, sortby = SlashOption(
    name = "sortby",
    choices = {
        "Treasury": "treasury",
        "Population": "population",
        "Total military units": "military"
    }
)):
    userlist = {}
    for user in db["users"].find():
        if user["_id"] == "placeholder":
            continue

        match sortby:
            case "treasury":
                val = user["treasury"]
            case "population":
                val = user["population"]
            case "military":
                val = 0
                for k, v in user["military"].items():
                    val += v

        userlist[user["name"]] = val
        userlist = dict(sorted(userlist.items(), key = lambda item: item[1], reverse = True))

    display = ""
    idx = 0
    for k, v in userlist.items():
        idx += 1
        match idx:
            case 1:
                if sortby == "treasury":
                    display += f":first_place: {k}: **${v:,}**\n"
                else:
                    display += f":first_place: {k}: **{v:,}**\n"
            case 2:
                if sortby == "treasury":
                    display += f":second_place: {k}: **${v:,}**\n"
                else:
                    display += f":second_place: {k}: **{v:,}**\n"
            case 3:
                if sortby == "treasury":
                    display += f":third_place: {k}: **${v:,}**\n"
                else:
                    display += f":third_place: {k}: **{v:,}**\n"
            case other:
                if sortby == "treasury":
                    display += f"**{idx}.** {k}: **${v:,}**\n"
                else:
                    display += f"**{idx}.** {k}: **{v:,}**\n"

    match sortby:
        case "treasury":
            lbtype = "Treasury"
        case "population":
            lbtype = "Population"
        case "military":
            lbtype = "Total Military Units"
    
    embed = nextcord.Embed(title = f"Leaderboard - {lbtype}", description = display, color = nextcord.Color.dark_purple())
    await interaction.response.send_message(embed = embed)

@client.slash_command(name = "daily", description = "View how your nation's economy and population has grown since the last daily.", guild_ids = GUILD_IDS)
async def daily(interaction: Interaction, user: nextcord.User = None):
    if user == None:
        user = interaction.user

    data = db["users"].find_one({"_id": user.id})
    embed = nextcord.Embed(title = "Daily", color = nextcord.Color.blue())
    embed.set_author(name = data["name"].title(), icon_url = user.avatar.url)
    embed.add_field(name = "💵 Economy", value = f"Income: ${data['lastdaily']['income']:,}\nExpenses: ${data['lastdaily']['expenses']:,}\n**Growth: ${data['lastdaily']['income'] - data['lastdaily']['expenses']:,}**", inline = False)
    embed.add_field(name = "👤 Population", value = f"Growth: +{data['lastdaily']['popgrowth']:,} **({data['population']:,})**", inline = False)

    await interaction.response.send_message(embed = embed)

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

# Im sick while writing this command it sucks
@client.slash_command(name = "research", description = "Use your research points", guild_ids = GUILD_IDS)
async def research(interaction: Interaction, path = SlashOption(
    name = "path",
    choices = {
        "⛏️ Mining": "mining",
        "🛢️ Oil Refinery": "oil_refinery",
        "🪨 Steel Refinery": "steel_refinery",
        "🌲 Forestry": "forestry",
        "✨ Development": "development"
    }
), amount: int = 1):
    userdata = db["users"].find_one({"_id": interaction.user.id})
    research_paths = userdata["research"]
    research_points = userdata["research_points"]

    if amount > research_points:
        embed = nextcord.Embed(title = "Not enough research points", description = f"You need **{amount - userdata['research_points']}** more research points.", color = nextcord.Color.red())
        ephemeral_message = True
    else:
        # Add points to the chosen research path
        research_points -= amount
        research_paths[path] += amount
        db["users"].update_one({"_id": interaction.user.id}, {"$set": {"research": research_paths, "research_points": research_points}})
        display_research = path.replace("_", " ")
        display_research = display_research.title()

        embed = nextcord.Embed(title = "Successfully used research points", description = f"You now have **{research_points}** research points.\n**{display_research}** was upgraded from **{research_paths[path] - amount}** to **{research_paths[path]}** (+{amount})", color = nextcord.Color.green())
        ephemeral_message = False

    await interaction.response.send_message(embed = embed, ephemeral = ephemeral_message)

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
        success = True
    else:
        embed = nextcord.Embed(title = ":x: Not enough money!", description = f"Your treasury doesn't have enough money to fulfil this purchase! You have **${userdata['treasury']:,}** but the purchase requires **${(shopitems[item]['cost'] * amount):,}**", color = nextcord.Color.red())
        success = False

    await interaction.response.send_message(embed = embed)
    await logmsg(f"Processed item purchase:\n- User purchasing: `{interaction.user.id}` ({userdata['name']})\n- Item: `{item}`\n- Amount: `{amount}`\n- Success: `{success}`", "buyitem")

@client.slash_command(name = "announce", guild_ids = GUILD_IDS)
async def announce(interaction: Interaction, message: str):
    if interaction.user.id == 687774746414546945:
        channel = client.get_channel(1065744269719113738)
        await channel.send(message)
    else:
        await interaction.response.send_message(embed = nextcord.Embed(title = "No perms bozo", description = "LLLLL", color = nextcord.Color.red()), ephemeral = True)

@client.slash_command(name = "reset", guild_ids = GUILD_IDS)
async def announce(interaction: Interaction):
    if interaction.user.id == 687774746414546945:
        for user in db["users"].find():
            db["users"].update_one({"_id": user["_id"]}, {"$set": {"population": 0}})
            db["users"].update_one({"_id": user["_id"]}, {"$set": {"treasury": 0}})
            db["users"].update_one({"_id": user["_id"]}, {"$set": {"research_points": 0}})
    else:
        await interaction.response.send_message(embed = nextcord.Embed(title = "No perms bozo", description = "LLLLL", color = nextcord.Color.red()), ephemeral = True)


# do something like this for money later https://stackoverflow.com/questions/63625246/discord-py-bot-run-function-at-specific-time-every-day
async def daily():
    while True:
        now = datetime.datetime.now()
        then = now + datetime.timedelta(days = 1)
        wait = (then - now).total_seconds()

        # Create embed
        embed = nextcord.Embed(title = "Daily income/population growth", description = f"Next daily <t:{int(time.mktime(then.timetuple()))}:R>\nUse `/daily` to check your nation's growth.")

        # Calculate income and population growth
        for user in db["users"].find():
            if user["_id"] == "placeholder":
                continue
            tax = user["population"] * user["tax_per_person"]
            income = tax
            income += random.randint(tax // 2, tax * 2)

            military_upkeep = (user["military"]["troops"] * 3) + (user["military"]["tanks"] * 1400) + (user["military"]["artillery"] * 150) + (user["military"]["frigates"] * 3300) + (user["military"]["destroyers"] * 6000) + (user["military"]["cruisers"] * 12000) + (user["military"]["submarines"] * 4500) + (user["military"]["fighter_aircraft"] * 600) + (user["military"]["bomber_aircraft"] * 1200) + (user["military"]["attack_aircraft"] * 800)
            administration = random.randint(1, 10) * user["population"]
            expenses = military_upkeep + administration

            # Grow population
            oldpop = user["population"]
            newpop = (user["population"] // 2) + (random.randint(1, 5) * (random.randint(1, 3) * user["research"]["development"])) + random.randint(-50, 50)
            db["users"].update_one({"_id": user["_id"]}, {"$set": {"population": oldpop + newpop}})

            db["users"].update_one({"_id": user["_id"]}, {"$set": {"treasury": user["treasury"] + (income - expenses)}})
            db["users"].update_one({"_id": user["_id"]}, {"$set": {"lastdaily": {"income": income, "expenses": expenses, "popgrowth": newpop}}})

            # Give research points
            db["users"].update_one({"_id": user["_id"]}, {"$set": {"research_points": user["research_points"] + 2}})

            await logmsg(f"Updated user {user['name']}", "daily")
            
        channel = client.get_channel(1065744269719113738)
        await channel.send("[ping goes here]", embed = embed)
        await logmsg(f"Finished calculating dailies for {now.day}/{now.month}/{now.year}", "daily")

        await asyncio.sleep(wait)

@client.event
async def on_ready():
    print("Bot is online")
    await logmsg("Bot started", "on_ready")
    await daily()

@client.event
async def on_error(error):
    await logmsg(f":x: ERROR: {str(error)}", "on_command_error")

client.run(tokens.client_token)