import discord
from discord import app_commands
import os
from dotenv import load_dotenv
from modules.AutoComplete import AutoComplete
from modules.PrizeSelector import PrizeSelector
from modules.BingoGenerator import BingoGenerator
from modules.Show import Show
from modules.Revealing import Reveal
from modules.Backup import Backup
from modules.BingoHandler import BingoHandler
from modules.Verify import Verify
ac = AutoComplete()
file_blacklist = ac.file_blacklist



load_dotenv()
mention_id = os.getenv("MENTION_ID")
sync_to_guild = discord.Object(id=os.getenv("TEST_GUILD"))
BotToken = os.getenv("TEST_TOKEN")
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
permission_error = "You are not allowed to call this function"

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('-------------------------------------------------')
    await tree.sync(guild=sync_to_guild) 

@tree.command(name="generate", description="Generates pairs of prizes/items", guild=sync_to_guild)
@app_commands.describe(amount="Number of item pairs to generate")
async def generate(interaction: discord.Interaction, amount: int):
    if interaction.user.guild_permissions.administrator:
        bingo_generator = BingoGenerator()
        bingo_generator.Generate(amount)
        await interaction.response.send_message(content=f"{amount} items/prizes generated.")
    else:
        await interaction.response.send_message(permission_error)

@tree.command(name="selectprize", description="Select a prize to add along with a random item to current board", guild=sync_to_guild)
@app_commands.describe(prize="What prize to add, must be exact name from /show prizes")
@app_commands.autocomplete(prize=ac.prize)
async def selectprize(interaction: discord.Interaction, prize: str):
    if interaction.user.guild_permissions.administrator:
        prize_selector = PrizeSelector()
        response = prize_selector.select_prize(prize)
        await interaction.response.send_message(response)
    else:
        await interaction.response.send_message(permission_error)

@tree.command(name="show", description="Show's Item/Prize lists", guild=sync_to_guild)
@app_commands.autocomplete(argument=ac.show)
async def show(interaction: discord.Interaction, argument: str):
    match argument.lower():
        case "prizes":
            show_prize = Show()
            response = show_prize.Prizes()
            embed = discord.Embed(title="List of available prizes", description=response)
            await interaction.user.send(embed=embed)
            await interaction.response.send_message("Check your DM's", ephemeral=True)
        case "items":
            show_item = Show()
            response = show_item.Items()
            embed = discord.Embed(title="List of available items", description=response)
            await interaction.user.send(embed=embed)
            await interaction.response.send_message("Check your DM's", ephemeral=True)
        case "generated":
            if interaction.user.guild_permissions.administrator:
                show_generated = Show()
                response = show_generated.Generated()
                if response != "Must generate items first.":
                    embed = discord.Embed(title=f"Generated Item/Prize pairs:", description=response)
                    await interaction.user.send(embed=embed)
                    await interaction.response.send_message("Check your DM's", ephemeral=True)
                else:
                    await interaction.response.send_message(response)
            else:
                await interaction.response.send_message(permission_error, ephemeral=True)
        case "revealed":
            show_revealed = Show()
            response = show_revealed.Revealed()
            if response != "No items have been revealed yet.":
                embed = discord.Embed(title="Revealed Tiles", description=response)
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(response)
        case _:
            await interaction.response.send_message("Please specify which list you wish to show.")
            
@tree.command(name="revealtile", guild=sync_to_guild)
async def revealtile(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:
        reveal = Reveal()
        response = reveal.Tile()
        embed = discord.Embed(title="Revealed Items", description=response)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(permission_error, ephemeral=True)
        
@tree.command(name="releaseboard", guild=sync_to_guild)
async def releaseboard(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:
        reveal = Reveal()
        response = reveal.Board()
        embed = discord.Embed(title="This months bingo board!", description=response)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(permission_error, ephemeral=True)
            
@tree.command(name="verify", guild=sync_to_guild)
@app_commands.describe(item="The item you wish to submit", screenshot="Chatbox confirming loot + RSN and Date. WIN + SHIFT + S for an easy screenshot.")
@app_commands.autocomplete(item=ac.item)
async def verify(interaction: discord.Interaction, item: str, screenshot: discord.Attachment):
    verifier = Verify()
    response = verifier.verify_drop(item=item)
    if response != False:
        embed = discord.Embed(title="BINGO!", description=f"{item} was on the list, you win {response}")
        embed.set_image(url=screenshot.url)
        await interaction.response.send_message(embed=embed)
        return
    else:
        embed = discord.Embed(title="LOSER...", description=f"{item} is not on the list, try again eh?")
        embed.set_image(url=screenshot.url)
        await interaction.response.send_message(embed=embed)
        return
        
@tree.command(name="additem", description="Add items to the items list", guild=sync_to_guild)
@app_commands.describe(item="item in lowercase without symbols to add")
async def additem(interaction: discord.Interaction, item: str):
    if interaction.user.guild_permissions.administrator:
        bh = BingoHandler()
        if bh.Additem(item):
            await interaction.response.send_message(f"Added [{item}] to items list")
        else:
            await interaction.response.send_message(f"[{item}] already exists.")
    else:
        await interaction.response.send_message(permission_error)

@tree.command(name="removeitem", description="Remove items from the items list", guild=sync_to_guild)
@app_commands.describe(item="item in lowercase without symbols to remove")
@app_commands.autocomplete(item=ac.item)
async def removeitem(interaction: discord.Interaction, item: str):
    if interaction.user.guild_permissions.administrator:
        bh = BingoHandler()
        if bh.Removeitem(item):
            await interaction.response.send_message(f"Removed [{item}] from items list")
        else:
            await interaction.response.send_message(f"[{item}] does not exist.")
    else:
        await interaction.response.send_message(permission_error)

@tree.command(name="addprize", description="Add prizes to the prize list", guild=sync_to_guild)
@app_commands.describe(prize="prize in lowercase to add")
async def addprize(interaction: discord.Interaction, prize: str):
    if interaction.user.guild_permissions.administrator:
        bh = BingoHandler()
        if bh.Addprize(prize):
            await interaction.response.send_message(f"Added [{prize}] to prize list")
        else:
            await interaction.response.send_message(f"[{prize}] already exists.")
    else:
        await interaction.response.send_message(permission_error)

@tree.command(name="removeprize", description="Remove prizes from the prize list", guild=sync_to_guild)
@app_commands.describe(prize="prize in lowercase to remove")
@app_commands.autocomplete(prize=ac.prize)
async def removeprize(interaction: discord.Interaction, prize: str):
    if interaction.user.guild_permissions.administrator:
        bh = BingoHandler()
        if bh.Removeprize(prize):
            await interaction.response.send_message(f"Removed [{prize}] from prize list")
        else:
            await interaction.response.send_message(f"[{prize}] does not exist.")
    else:
        await interaction.response.send_message(permission_error)

@tree.command(name="backup", description="Backup current bingo to file", guild=sync_to_guild)
@app_commands.describe(filename="What you want to call the file, cannot contain [,./\()?!=+#""@]")
async def backup(interaction: discord.Interaction, filename: str):
    if interaction.user.guild_permissions.administrator:
        bk = Backup()
        if bk.Create(filename):
            await interaction.response.send_message(f"Backup {filename} created.")
        else:
            await interaction.response.send_message(f"Blacklisted filename, try with a different name.")
    else:
        await interaction.response.send_message(permission_error)

@tree.command(name="loadbackup", description="Loads a bingo file from backup", guild=sync_to_guild)
@app_commands.describe(filename="Which bingo file to fetch from backup.")
@app_commands.autocomplete(filename=ac.backup)
async def loadbackup(interaction: discord.Interaction, filename: str):
    if interaction.user.guild_permissions.administrator:
        bk = Backup()
        if bk.Load(filename):
            await interaction.response.send_message(f"Loaded {filename} from backup.")
        else:
            await interaction.response.send_message(f"{filename} does not exist or exists as a blacklisted file.")
    else:
        await interaction.response.send_message(permission_error)

@tree.command(name="listbackups", description="Returns a list of filenames for previous backups stored.", guild=sync_to_guild)
@app_commands.describe()
async def listbackups(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:
        bk = Backup()
        response = bk.List()
        await interaction.response.send_message(response)
    else:
        await interaction.response.send_message("No backups currently exist.")

@tree.command(name="removebackup", description="Removes backup files.", guild=sync_to_guild)
@app_commands.describe(filename="Which file to delete")
@app_commands.autocomplete(filename=ac.backup)
async def removebackup(interaction: discord.Interaction, filename: str):
    if interaction.user.guild_permissions.administrator:
        bk = Backup()
        if bk.Remove(filename):
            await interaction.response.send_message(f"Backup {filename} removed from stored backups")
        else:
            await interaction.response.send_message(f"{filename} doesnt exist or exists as a blacklisted file")
    else:
        await interaction.response.send_message(permission_error)

@tree.command(name="help", description="tip#1: Don't let mea anywhere near admin tools.", guild=sync_to_guild)
@app_commands.describe(command="Which command to see help for, {default=all}")
@app_commands.autocomplete(command=ac.command)
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