# Description: Main file for the Bingo Bot project. This file contains the main functions for the bot to run.
from datetime import datetime

import discord
from discord import app_commands
import os

from collections import defaultdict, Counter
from dotenv import load_dotenv
load_dotenv()

from src.modules.BingoGenerator import BingoGenerator
from src.modules.PrizeSelector import PrizeSelector
from src.modules.EntryHandler import EntryHandler
from src.modules.Show import Show
from src.modules.Revealing import Reveal
from src.modules.Backup import Backup
from src.modules.AutoComplete import AutoComplete
from src.modules.Verify import Verify


PERMISSION_ERROR = "You are not allowed to call this function"
NUKE_LIST = ["[", "]", "{", "}", ",", "'"]
MENTION_ID = os.getenv("MENTION_ID")
SYNC_GUILD = discord.Object(id=os.getenv("LIVE_GUILD"))
TEST_CHANNEL = int(os.getenv("TEST_CHANNEL"))
BINGO_CHANNEL = int(os.getenv("BINGO_CHANNEL"))
FILE_BLACKLIST = os.getenv("FILE_BLACKLIST")
BOT_TOKEN = os.getenv("LIVE_TOKEN")
INTENTS = discord.Intents.all()
client = discord.Client(intents=INTENTS)
tree = app_commands.CommandTree(client)
current_name = ""
generated_items = []
user_counters = defaultdict(Counter)
ac = AutoComplete()

async def command_tracker(interaction: discord.Interaction):
    user_id = interaction.user
    user_counters[user_id]["verify"] += 1
    print(user_counters[user_id]["verify"])

    if user_counters[user_id]["verify"] % 3 == 0:
        print(f"{user_id} has called verify {user_counters[user_id]['verify']} times")
        await release_tile(interaction)

    return user_counters[user_id]["verify"]
    
def reset_tracker():
    user_counters.clear()

async def release_tile(interaction: discord.Interaction):
        tiles = Reveal()
        revealed_tiles = tiles.tile()
        if revealed_tiles:
            await interaction.channel.send(content=f"**{interaction.user} just revealed a new tile:**\n{revealed_tiles}")
        else:
            await interaction.channel.send(content="**All tiles have been revealed!**")


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('-------------------------------------------------')
    await tree.sync(guild=SYNC_GUILD)
    await client.change_presence(activity=discord.Game(name="Bingo!", start=datetime.utcnow()))
    #await client.get_channel(TEST_CHANNEL).send(f"Bot is online, use /help for commands")
    await client.get_channel(BINGO_CHANNEL).send(f"Bot is online, use /help for commands")

@tree.command(name="shutdown", guild=SYNC_GUILD)
async def shutdown(interaction: discord.Interaction):
    if interaction.user.id == 225683257146998785:
        await interaction.channel.send("Shutting Down for Maintenance")
        await interaction.response.send_message("Shutting Down for Maintenance", ephemeral=True)
        exit()
    else:
        await interaction.response.send_message(PERMISSION_ERROR, ephemeral=True)

@tree.command(name="generate",description="Generates pairs of prizes/items", guild=SYNC_GUILD)
@app_commands.describe(amount="Number of item pairs to generate")
async def generate(interaction: discord.Interaction, amount: int):
    if interaction.user.guild_permissions.administrator:
        generator = BingoGenerator()
        generator.generate(amount)
        await interaction.response.send_message(content=f"{amount} items/prizes generated.")
        reset_tracker()
        return
    else:
        await interaction.response.send_message(PERMISSION_ERROR)

@tree.command(name="selectprize",description="Select a prize to add along with a random item to current board", guild=SYNC_GUILD)
@app_commands.describe(prize="What prize to add, must be exact name from /show prizes")
@app_commands.autocomplete(prize=ac.prize)
async def selectprize(interaction: discord.Interaction, prize: str):
    if interaction.user.guild_permissions.administrator:
        prize_selector = PrizeSelector()
        try:
            new_prize, new_item = prize_selector.select_prize(prize)
            await interaction.response.send_message(f"added {new_prize} and {new_item} to board")
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}")
    else:
        await interaction.response.send_message(PERMISSION_ERROR)

@tree.command(name="show", description="Show's Item/Prize lists", guild=SYNC_GUILD)
@app_commands.autocomplete(argument=ac.show)
async def show(interaction: discord.Interaction, argument: str):
    show = Show()
    match argument.lower():
        case "revealed":
            embed_description = show.revealed()
            embed = discord.Embed(title="**Revealed Tiles**", description=embed_description)
            await interaction.response.send_message(embed=embed)
        case "prizes":
            embed_description = show.prizes()
            embed = discord.Embed(title="List of available prizes", description=embed_description)
            await interaction.user.send(embed=embed)
            await interaction.response.send_message("Check your DM's", ephemeral=True)
        case "items":
            embed_description = show.items()
            embed = discord.Embed(title="List of available items", description=embed_description)
            await interaction.user.send(embed=embed)
            await interaction.response.send_message("Check your DM's", ephemeral=True)
        case "generated":
            if interaction.user.guild_permissions.administrator:
                try:
                    embed_description = show.generated()
                    embed = discord.Embed(title=f"Generated Item/Prize pairs:", description=embed_description)
                    await interaction.user.send(embed=embed)
                    await interaction.response.send_message("Check your DM's", ephemeral=True)
                except:
                    await interaction.response.send_message("Must generate items first.")
            else:
                await interaction.response.send_message(PERMISSION_ERROR, ephemeral=True)
        case _:
            await interaction.response.send_message("Please specify which list you wish to show.")
            
@tree.command(name="revealtile", guild=SYNC_GUILD)
async def revealtile(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:
        tiles = Reveal()
        embed_description = tiles.tile()
        if embed_description:
            await interaction.response.send_message(f"**Revealed tiles are:**\n{embed_description}")
        else:
            await interaction.response.send_message("No more tiles to reveal", ephemeral=True)
    else:
        await interaction.response.send_message(PERMISSION_ERROR, ephemeral=True)
        
@tree.command(name="releaseboard", guild=SYNC_GUILD)
async def releaseboard(interaction: discord.Interaction):
    release = Reveal()
    if interaction.user.guild_permissions.administrator:
        embed_description = release.board()
        embed_description.translate(NUKE_LIST)
        embed = discord.Embed(title="This months bingo board!", description=embed_description)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(PERMISSION_ERROR, ephemeral=True)
            
@tree.command(name="verify", guild=SYNC_GUILD)
@app_commands.describe(item="The item you wish to submit",
                        screenshot="Chatbox confirming loot + RSN and Date. WIN + SHIFT + S for an easy screenshot.")
@app_commands.autocomplete(item=ac.item)
async def verify(interaction: discord.Interaction, item: str, screenshot: discord.Attachment):
    await command_tracker(interaction)
    verifier = Verify()
    check_item = verifier.verify_drop(item)
    print(check_item)
    if check_item:
        won_item = str(check_item["item"])
        won_prize = str(check_item["prize"])
        embed = discord.Embed(title="BINGO!", description=f"[{won_item.capitalize()}] you win! [{won_prize.capitalize()}]  |  {MENTION_ID} will pay out shortly")
        embed.set_image(url=screenshot.url)
        await interaction.response.send_message(embed=embed)

    else:
        embed = discord.Embed(title=f"LOSER... {item} was not on the list this time.")
        embed.set_image(url=screenshot.url)
        await interaction.response.send_message(embed=embed)


@tree.command(name="additem", description="Add items to the items list", guild=SYNC_GUILD)
@app_commands.describe(item="item in lowercase without symbols to add")
async def additem(interaction: discord.Interaction, item: str):
    handler = EntryHandler()
    if interaction.user.guild_permissions.administrator:
        if handler.add_item(item):
            await interaction.response.send_message(f"Added [{item}] to items list")
        else:
            await interaction.response.send_message(f"[{item}] already exists on the list")
    else:
        await interaction.response.send_message(PERMISSION_ERROR)


@tree.command(name="removeitem", description="Remove items from the items list", guild=SYNC_GUILD)
@app_commands.describe(item="item in lowercase without symbols to remove")
@app_commands.autocomplete(item=ac.item)
async def removeitem(interaction: discord.Interaction, item: str):
    handler = EntryHandler()
    if interaction.user.guild_permissions.administrator:
        if handler.remove_item(item):
            await interaction.response.send_message(f"Removed [{item}] from items list")
        else:
            await interaction.response.send_message(f"[{item}] does not exist on the list")
    else:
        await interaction.response.send_message(PERMISSION_ERROR)

@tree.command(name="addprize", description="Add prizes to the prize list", guild=SYNC_GUILD)
@app_commands.describe(prize="prize in lowercase to add")
async def addprize(interaction: discord.Interaction, prize: str):
    handler = EntryHandler()
    if interaction.user.guild_permissions.administrator:
        if handler.add_prize(prize):
            await interaction.response.send_message(f"Added [{prize}] to prize list")
        else:
            await interaction.response.send_message(f"[{prize}] already exists on the list")
    else:
        await interaction.response.send_message(PERMISSION_ERROR)

@tree.command(name="removeprize", description="Remove prizes from the prize list", guild=SYNC_GUILD)
@app_commands.describe(prize="prize in lowercase to remove")
@app_commands.autocomplete(prize=ac.prize)
async def removeprize(interaction: discord.Interaction, prize: str):
    handler = EntryHandler()
    if interaction.user.guild_permissions.administrator:
        if handler.remove_prize(prize):
            await interaction.response.send_message(f"Removed [{prize}] from prize list")
        else:
            await interaction.response.send_message(f"[{prize}] does not exist on the list")
    else:
        await interaction.response.send_message(PERMISSION_ERROR)

@tree.command(name="backup", description="Backup current bingo to file", guild=SYNC_GUILD)
@app_commands.describe(filename="What you want to call the file, cannot contain [,. /\()?!=+#""@]")
async def backup(interaction: discord.Interaction, filename: str):
    backup = Backup()
    if interaction.user.guild_permissions.administrator:
        try:
            backup.create(filename)
            await interaction.response.send_message(f"Backup {filename} created.")
        except Exception as e:
            await interaction.response.send_message(f"Error creating backup: {e}")
    else:
        await interaction.response.send_message(PERMISSION_ERROR)

@tree.command(name="load", description="Loads a bingo file from backup", guild=SYNC_GUILD)
@app_commands.describe(filename="Which bingo file to fetch from backup.")
@app_commands.autocomplete(filename=ac.backup)
async def load(interaction: discord.Interaction, filename: str):
    if interaction.user.guild_permissions.administrator:
        try:
            backup = Backup()
            backup.load(filename)
            await interaction.response.send_message(f"Loaded {backup} from backup.")
        except Exception as e:
            await interaction.response.send_message(f"Error loading backup: {e}")
        else:
            await interaction.response.send_message(f"{filename} does not exist as a valid backup.")
    else:
        await interaction.response.send_message(PERMISSION_ERROR)

@tree.command(name="listbackups", description="Returns a list of filenames for previous backups stored.", guild=SYNC_GUILD)
@app_commands.describe()
async def listbackups(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:
        backup = Backup()
        backup_list = backup.list()
        if backup_list:
            await interaction.response.send_message(backup_list)
        else:
            await interaction.response.send_message("No backups currently stored on file")

@tree.command(name="removebackup", description="Removes backup files.", guild=SYNC_GUILD)
@app_commands.describe(filename="Which file to delete")
@app_commands.autocomplete(filename=ac.backup)
async def removebackup(interaction: discord.Interaction, filename: str):
    if interaction.user.guild_permissions.administrator:
        backup = Backup()
        try:
            backup.remove(filename)
            await interaction.response.send_message(f"Backup {filename} removed from stored backups")
        except Exception as e:
            await interaction.response.send_message(f"Error removing backup: {e}")
    else:
        await interaction.response.send_message(PERMISSION_ERROR)



@tree.command(name="help", description="tip#1: Don't let mea anywhere near admin tools.", guild=SYNC_GUILD)
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

client.run(BOT_TOKEN)

