import json
import discord
import random
from discord import app_commands
import os
from dotenv import load_dotenv
load_dotenv()

mention_id = os.getenv("MENTION_ID")
sync_to_guild = discord.Object(id=os.getenv("TEST_GUILD"))
BotToken = os.getenv("TEST_TOKEN")
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
file_blacklist = os.getenv("FILE_BLACKLIST")
permission_error = "You are not allowed to call this function"
current_name = ""
generated_items = []
revealedtiles = ""
nuke_list = ["[", "]", "{", "}", ",", "'"]
not_revealed = ""

async def item_autocomplete(interaction: discord.Interaction, current: str,) -> list[app_commands.Choice[str]]:
    with open("items.json", "r") as f:
        items = json.load(f)
        return [
            app_commands.Choice(name=item, value=item)
            for item in items if current.lower() in item.lower()
        ]
async def prize_autocomplete(interaction: discord.Interaction, current: str,) -> list[app_commands.Choice[str]]:
    with open("prizes.json", "r") as f:
        prizes = json.load(f)
        return [
            app_commands.Choice(name=prize, value=prize)
            for prize in prizes if current.lower() in prize.lower()
        ]
async def show_autocomplete(interaction: discord.Interaction, current: str,) -> list[app_commands.Choice[str]]:
    choices = ["prizes", "items", "generated", "revealed"]
    return [
        app_commands.Choice(name=argument, value=argument)
        for argument in choices if current.lower() in argument.lower()
    ]

async def command_autocomplete(interaction: discord.Interaction, current: str,) -> list[app_commands.Choice[str]]:
    choices = ["all","generate", "selectprize", "show", "verify", "additem", "removeitem", "addprize", "removeprize", "backup", "load", "listbackups", "removebackup", "revealtile", "releaseboard"]
    return [
        app_commands.Choice(name=command, value=command)
        for command in choices if current.lower() in command.lower()
    ]

async def backup_autocomplete(interaction: discord.Interaction, current: str,) -> list[app_commands.Choice[str]]:
    choices = []
    directory = "."
    file_type = (".json")
    choices += ([backup[:-5] for backup in os.listdir(directory) if backup.endswith(file_type) and backup not in file_blacklist])
    return [
        app_commands.Choice(name=filename, value=filename)
        for filename in choices if current.lower() in filename.lower()
]

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('-------------------------------------------------')
    await tree.sync(guild=sync_to_guild) 


@tree.command(name="generate",description="Generates pairs of prizes/items", guild=sync_to_guild)
@app_commands.describe(amount="Number of item pairs to generate")
async def generate(interaction: discord.Interaction, amount: int):
    if interaction.user.guild_permissions.administrator:
        with open("prizes.json", "r") as f:
            prizes = json.load(f)
        with open("items.json", "r") as f:
            items = json.load(f)
        random_items = random.sample(items, k=amount)
        random_prizes = random.sample(prizes, k=amount)
        for i in range(amount):
            generated_items.append((random_items[i], random_prizes[i]))
        await interaction.response.send_message(content=f"{amount} items/prizes generated.")
        global not_revealed
        not_revealed = [i[0] for i in generated_items]
        return generated_items, not_revealed
    else:
        await interaction.response.send_message(permission_error)

@tree.command(name="selectprize",description="Select a prize to add along with a random item to current board", guild=sync_to_guild)
@app_commands.describe(prize="What prize to add, must be exact name from /show prizes")
@app_commands.autocomplete(prize=prize_autocomplete)
async def selectprize(interaction: discord.Interaction, prize: str):
    if interaction.user.guild_permissions.administrator:
        try:
            with open("prizes.json", "r") as f:
                prizes = json.load(f)
            with open("items.json", "r") as f:
                items = json.load(f)
            for item in prizes:
                if item == prize:
                    selected_item = random.choice(items)
                    new_items = (selected_item, prize)
                    generated_items.append(new_items)
                    global not_revealed
                    not_revealed = [i[0] for i in generated_items]
                    await interaction.response.send_message(f"added {prize} and {selected_item}")
                    return not_revealed, generated_items
        except NameError:
            await interaction.response.send_message("Must generate list first!")
    else:
        await interaction.response.send_message(permission_error)

@tree.command(name="show", description="Show's Item/Prize lists", guild=sync_to_guild)
@app_commands.autocomplete(argument=show_autocomplete)
async def show(interaction: discord.Interaction, argument: str):
    match argument.lower():
        case "revealed":
            embed = discord.Embed(title="**Revealed Tiles**", description=revealedtiles)
            await interaction.response.send_message(embed=embed)
        case "prizes":
            with open("prizes.json", "r") as f:
                prizes = json.load(f)
            embed_description = ""
            for prize in prizes:
                embed_description += f"{prize} \n"
            embed = discord.Embed(title="List of available prizes", description=embed_description)
            await interaction.user.send(embed=embed)
            await interaction.response.send_message("Check your DM's", ephemeral=True)
        case "items":
            with open("items.json", "r") as f:
                items = json.load(f)
            embed_description = ""
            for item in items:
                embed_description += f"{item} \n"
            embed = discord.Embed(title="List of available items", description=embed_description)
            await interaction.user.send(embed=embed)
            await interaction.response.send_message("Check your DM's", ephemeral=True)
        case "generated":
            if interaction.user.guild_permissions.administrator:
                try:
                    embed_description = ""
                    for item in generated_items:
                        embed_description += f"{item} \n"
                    embed = discord.Embed(title=f"Generated Item/Prize pairs:", description=embed_description)
                    await interaction.user.send(embed=embed)
                    await interaction.response.send_message("Check your DM's", ephemeral=True)
                except:
                    await interaction.response.send_message("Must generate items first.")
            else:
                await interaction.response.send_message(permission_error, ephemeral=True)
        case _:
            await interaction.response.send_message("Please specify which list you wish to show.")
            
@tree.command(name="revealtile", guild=sync_to_guild)
async def revealtile(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:
        global not_revealed
        global revealedtiles
        print(not_revealed)
        if len(not_revealed) > 0:
            to_reveal = random.choice(not_revealed)
            not_revealed.remove(to_reveal)
            item_to_str = "".join(map(str, to_reveal))
            to_reveal = item_to_str
            to_reveal = to_reveal.translate(nuke_list)
            to_reveal = to_reveal.title()
            revealedtiles += f"{to_reveal}\n"
            await interaction.response.send_message(f"**Revealed tiles are:**\n{revealedtiles}")
            return revealedtiles, not_revealed
        else:
            await interaction.response.send_message("No more tiles to reveal", ephemeral=True)
    else:
        await interaction.response.send_message(permission_error, ephemeral=True)
        
@tree.command(name="releaseboard", guild=sync_to_guild)
async def releaseboard(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:
        message_string = ""
        for item,prize in generated_items:
            item_to_str = "".join(map(str, item))
            item = item_to_str
            item = item.title()
            message_string += (f"{item} : {prize}\n")
            message_string.translate(nuke_list)
        embed = discord.Embed(title="This months bingo board!", description=message_string)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(permission_error, ephemeral=True)
            
@tree.command(name="verify", guild=sync_to_guild)
@app_commands.describe(item="The item you wish to submit", screenshot="Chatbox confirming loot + RSN and Date. WIN + SHIFT + S for an easy screenshot.")
@app_commands.autocomplete(item=item_autocomplete)
async def verify(interaction: discord.Interaction, item: str, screenshot: discord.Attachment):
    if item not in [i[0] for i in generated_items]:
        embed = discord.Embed(title=f"LOSER... {item} was not on the list this time.")
        embed.set_image(url=screenshot.url)
        await interaction.response.send_message(embed=embed)
    else:
        for items, prizes in generated_items:
            if item == items:
                remove_tuple = items, prizes
                item = item.upper()
                embed = discord.Embed(title="BINGO!", description=f"{item} you win! [{prizes}]  |  {mention_id} will pay out shortly")
                embed.set_image(url=screenshot.url)
                await interaction.response.send_message(embed=embed)
                generated_items.remove(remove_tuple)
                with open("prizes.json", "r") as f:
                    data = json.load(f)
                    data.remove(prizes.lower())
                    data.sort()
                with open("prizes.json", "w") as f:
                    json.dump(data, f, indent=4)
                return generated_items

@tree.command(name="additem", description="Add items to the items list", guild=sync_to_guild)
@app_commands.describe(item="item in lowercase without symbols to add")
async def additem(interaction: discord.Interaction, item: str):
    if interaction.user.guild_permissions.administrator:
        with open("items.json", "r") as f:
            data = json.load(f)
            if item not in data:
                data.append(item)
                data.sort()
                with open("items.json", "w") as f:
                    json.dump(data, f, indent=4)
                    await interaction.response.send_message(f"Added [{item}] to items list")
            else:
                await interaction.response.send_message(f"[{item}] already exists on the list")
    else:
        await interaction.response.send_message(permission_error)


@tree.command(name="removeitem", description="Remove items from the items list", guild=sync_to_guild)
@app_commands.describe(item="item in lowercase without symbols to remove")
@app_commands.autocomplete(item=item_autocomplete)
async def removeitem(interaction: discord.Interaction, item: str):
    if interaction.user.guild_permissions.administrator:
        with open("items.json", "r") as f:
            data = json.load(f)
            if item in data:
                data.remove(item)
                data.sort()
                with open("items.json", "w") as f:
                    json.dump(data, f, indent=4)
                    await interaction.response.send_message(f"Removed [{item}] from items list")
            else:
                await interaction.response.send_message(f"[{item}] does not exist on the list")
    else:
        await interaction.response.send_message(permission_error)

@tree.command(name="addprize", description="Add prizes to the prize list", guild=sync_to_guild)
@app_commands.describe(prize="prize in lowercase to add")
async def addprize(interaction: discord.Interaction, prize: str):
    if interaction.user.guild_permissions.administrator:
        with open("prizes.json", "r") as f:
            data = json.load(f)
            if prize not in data:
                data.append(prize)
                data.sort()
                with open("prizes.json", "w") as f:
                    json.dump(data, f, indent=4)
                    await interaction.response.send_message(f"Added [{prize}] to prize list")
            else:
                await interaction.response.send_message(f"[{prize}] already exists on the list")
    else:
        await interaction.response.send_message(permission_error)

@tree.command(name="removeprize", description="Remove prizes from the prize list", guild=sync_to_guild)
@app_commands.describe(prize="prize in lowercase to remove")
@app_commands.autocomplete(prize=prize_autocomplete)
async def removeprize(interaction: discord.Interaction, prize: str):
    if interaction.user.guild_permissions.administrator:
        with open("prizes.json", "r") as f:
            data = json.load(f)
            if prize in data:
                data.remove(prize)
                data.sort()
                with open("prizes.json", "w") as f:
                    json.dump(data, f, indent=4)
                    await interaction.response.send_message(f"Removed [{prize}] from prize list")
            else:
                await interaction.response.send_message(f"[{prize}] does not exist on the list")
    else:
        await interaction.response.send_message(permission_error)

@tree.command(name="backup", description="Backup current bingo to file", guild=sync_to_guild)
@app_commands.describe(filename="What you want to call the file, cannot contain [,. /\()?!=+#""@]")
async def backup(interaction: discord.Interaction, filename: str):
    if interaction.user.guild_permissions.administrator and filename not in file_blacklist:
        new_backup = f"{filename}.json"
        with open(new_backup, "w") as f:
            json.dump(generated_items, f, indent=4)
        await interaction.response.send_message(f"Backup {filename} created.")
    else:
        await interaction.response.send_message(permission_error)

@tree.command(name="load", description="Loads a bingo file from backup", guild=sync_to_guild)
@app_commands.describe(filename="Which bingo file to fetch from backup.")
@app_commands.autocomplete(filename=backup_autocomplete)
async def load(interaction: discord.Interaction, filename: str):
    if interaction.user.guild_permissions.administrator:
        if os.path.exists(f"{filename}.json") and filename not in file_blacklist:
            backup = f"{filename}.json"
            with open(backup) as f:
                current_name = filename
                generated_items = json.load(f)
            await interaction.response.send_message(f"Loaded {backup} from backup.")
            return current_name, generated_items
        else:
            await interaction.response.send_message(f"{filename} does not exist as a valid backup.")
    else:
        await interaction.response.send_message(permission_error)

@tree.command(name="listbackups", description="Returns a list of filenames for previous backups stored.", guild=sync_to_guild)
@app_commands.describe()
async def listbackups(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:
        directory = "."
        file_type = (".json")
        backups = [backup[:-5] for backup in os.listdir(directory) if backup.endswith(file_type) and backup not in file_blacklist]
        backup_list = ""
        for backup in backups:
            backup_list += f"{backup} \n"
        if backup_list:
            await interaction.response.send_message(backup_list)
        else:
            await interaction.response.send_message("No backups currently stored on file")

@tree.command(name="removebackup", description="Removes backup files.", guild=sync_to_guild)
@app_commands.describe(filename="Which file to delete")
@app_commands.autocomplete(filename=backup_autocomplete)
async def removebackup(interaction: discord.Interaction, filename: str):
    if interaction.user.guild_permissions.administrator and filename not in file_blacklist:
        directory = "."
        file_type = (".json")
        backups = [backup[:-5] for backup in os.listdir(directory) if backup.endswith(file_type) and backup not in file_blacklist]
        if filename in backups:
            os.remove(f"{filename}.json")
            await interaction.response.send_message(f"Backup {filename} removed from stored backups")
        else:
            await interaction.response.send_message(f"{filename} doesnt exist or is NoneType")
    else:
        await interaction.response.send_message(permission_error)



@tree.command(name="help", description="tip#1: Don't let mea anywhere near admin tools.", guild=sync_to_guild)
@app_commands.describe(command="Which command to see help for, {default=all}")
@app_commands.autocomplete(command=command_autocomplete)
async def help(interaction: discord.Interaction, command: str):
    
    match command.lower():
        
        case "verify":
            embed = discord.Embed(title=f"Help screen for {command.capitalize()}", description=f"{command.capitalize()} takes two positional arguments [drop] and [attachement] used to verify if the drop you received matches one of the winning items/prizes")
            await interaction.response.send_message(embed=embed)

        case "show":
            embed = discord.Embed(title=f"Help screen for {command.capitalize()}", description=f"{command.capitalize()} takes one positional argument [argument] this is used to determine which action runs, options are [items][prizes][revealed] and [generated] which is admin only.")
            await interaction.response.send_message(embed=embed)

        case "generate":
            embed = discord.Embed(title=f"Help screen for {command.capitalize()}", description=f"{command.capitalize()} takes two positional arguments [amount] and [name] these arguments control the [amount] of items generated and the [name] of that set of generated items. Both are required. admin only.")
            await interaction.response.send_message(embed=embed)

        case "additem" | "addprize":
            embed = discord.Embed(title=f"Help screen for {command.capitalize()}", description=f"{command.capitalize()} takes one positional argument [item] or [prize] this is used to determine which item/prize is added to the list of items/prizes this command is admin only.")
            await interaction.response.send_message(embed=embed)

        case "removeitem" | "removeprize":
            embed = discord.Embed(title=f"Help screen for {command.capitalize()}", description=f"{command.capitalize()} takes one positional argument [item] or [prize] this is used to determine which item/prize is removed from the list of items/prizes this command is admin only.")
            await interaction.response.send_message(embed=embed)

        case "selectprize":
            embed = discord.Embed(title=f"Help screen for {command.capitalize()}", description=f"{command.capitalize()} takes one positional argument [prize] this is used to determine which prize is added to the list of generated items/prizes, randomly selects an item. command is admin only.")
            await interaction.response.send_message(embed=embed)

        case "backup":
            embed = discord.Embed(title=f"Help screen for {command.capitalize()}", description=f"{command.capitalize()} takes one positional argument [filename] this is used to set the filename for the backup. command is admin only.")
            await interaction.response.send_message(embed=embed)

        case "load":
            embed = discord.Embed(title=f"Help screen for {command.capitalize()}", description=f"{command.capitalize()} takes one positional argument [filename] this is used to look for the file for the backup. command is admin only.")
            await interaction.response.send_message(embed=embed)

        case "listbackups":
            embed = discord.Embed(title=f"Help screen for {command.capitalize()}", description=f"{command.capitalize()} takes no arguments. Shows a list of existing backup filenames. command is admin only.")
            await interaction.response.send_message(embed=embed)

        case "removebackup":
            embed = discord.Embed(title=f"Help screen for {command.capitalize()}", description=f"{command.capitalize()} takes one positional argument [filename] this is used to look for the file to remove from backups directory. command is admin only.")
            await interaction.response.send_message(embed=embed)
            
        case "revealtile":
            embed = discord.Embed(title=f"Help screen for {command.capitalize()}", description=f"{command.capitalize()} reveals a bingo item at random. command is admin only.")
            await interaction.response.send_message(embed=embed)
        
        case "releaseboard":
            embed = discord.Embed(title=f"Help screen for {command.capitalize()}", description=f"{command.capitalize()} reveals the current board to participants, including prizes. command is admin only.")
            await interaction.response.send_message(embed=embed)
        
        case "all" | _:
            embed = discord.Embed(title="Help screen for Mystery Bingo", description="List of available commands.")
            embed.add_field(name="/verify", value="Submit your loot! This command requires you select what your drop is and attach a screenshot.")
            embed.add_field(name="/show", value="Lets you view what items/prizes exist or revealed tiles. [items][prizes][revealed]")
            embed.add_field(name="\u200b", value="\u200b")
            embed.add_field(name="\u200b", value="\u200b")
            embed.add_field(name="Admin Commands", value="\u200b")
            embed.add_field(name="\u200b", value="\u200b")
            embed.add_field(name="/generate", value="Generates a set of items/prizes for this month, takes [amount] and [name] as arguments.")
            embed.add_field(name="/add[item/prize]", value="Adds items/prizes to the list of allowed items/prizes")
            embed.add_field(name="/remove[item/prize]", value="Removes items/prizes from the list of allowed items/prizes")
            embed.add_field(name="/selectprize", value="Select a prize to add with a random item to the board")
            embed.add_field(name="/show [generated]", value="Admin argument to show active bingo items/prizes.")
            embed.add_field(name="/backup", value="Writes current bingo items/prizes to file using [filename] argument, can be loaded using /load [backup]")
            embed.add_field(name="/load", value="Loads backup from file, takes [filename] as argument.")
            embed.add_field(name="/listbackups", value="Lists currently available backups from file.")
            embed.add_field(name="/removebackup", value="Removes a backup if it exists on file.")
            embed.add_field(name="/revealtile", value="Reveals a random item from current bingo board")
            embed.add_field(name="/releaseboard", value="Releases current board to participants, including prizes.")
            await interaction.response.send_message(embed=embed)

client.run(BotToken)

