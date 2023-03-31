import discord
from discord import app_commands
import json
import os



class AutoComplete:
    def __init__(self):
        self.file_blacklist = ["items.json",
                                "generated.json",
                                "not_revealed.json",
                                "prizes.json",
                                "revealed.json"
        ]
    
    
    async def item(self, interaction: discord.Interaction, current: str,) -> list[app_commands.Choice[str]]:
        with open("src/Json/items.json", "r") as f:
            items = json.load(f)
        choices = [
            app_commands.Choice(name=item, value=item)
            for item in items if current.lower() in item.lower()]
        print(f"{interaction.user.display_name} is typing...")
        return choices[:25]

    async def prize(self, interaction: discord.Interaction, current: str,) -> list[app_commands.Choice[str]]:
        with open("src/Json/prizes.json", "r") as f:
            prizes = json.load(f)
            choices = [
                app_commands.Choice(name=prize, value=prize)
                for prize in prizes if current.lower() in prize.lower()]
            print(f"{interaction.user.display_name} is typing...")
            return choices[:25]
    
    async def show(self, interaction: discord.Interaction, current: str,) -> list[app_commands.Choice[str]]:
        choices = ["prizes", "items", "generated", "revealed"]
        print(f"{interaction.user.display_name} is typing...")
        return [
            app_commands.Choice(name=argument, value=argument)
            for argument in choices if current.lower() in argument.lower()]

    async def command(self, interaction: discord.Interaction, current: str,) -> list[app_commands.Choice[str]]:
        choices = ["all","generate", "selectprize", "show", "verify", "additem", "removeitem", "addprize", "removeprize", "backup", "load", "listbackups", "removebackup", "revealtile", "releaseboard"]
        print(f"{interaction.user.display_name} is typing...")
        return [
            app_commands.Choice(name=command, value=command)
            for command in choices if current.lower() in command.lower()]
    
    async def backup(self, interaction: discord.Interaction, current: str,) -> list[app_commands.Choice[str]]:
        choices = []
        file_type = (".json")
        choices += ([backup[:-5] for backup in os.listdir(path="src/Json") if backup.endswith(file_type) and backup not in self.file_blacklist])
        print(f"{interaction.user.display_name} is typing...")
        return [app_commands.Choice(name=filename, value=filename) for filename in choices if current.lower() in filename.lower()]