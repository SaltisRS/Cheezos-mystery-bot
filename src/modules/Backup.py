import json
from re import T
from .GenerationEncoder import GenerationEncoder
import os

class Backup:
    def __init__(self):
        self.directory = "src/Json"
        self.file_type = (".json")
        self.file_blacklist = ["items.json",
        "generated.json",
        "not_revealed.json",
        "prizes.json",
        "revealed.json"]
        with open("src/Json/generated.json", "r") as f:
            self.new_backup = json.load(f)
        self.not_revealed = []
        self.backup_list = ""
        
    def create(self, filename):
        if filename not in self.file_blacklist:
            file = f"src/Json{filename}.json"
            with open(file, "w") as f:
                json.dump(self.new_backup, f, indent=4, cls=GenerationEncoder)
            return
        else:
            raise ValueError(f"Cannot create backup with names {self.file_blacklist}!")
            
    def load(self, filename):
        if os.path.exists(f"src/Json/{filename}.json") and filename not in self.file_blacklist:
            backup = f"src/Json/{filename}.json"
            with open(backup, "r") as f:
                from_backup = json.load(f)
            with open("src/Json/generated.json", "w") as f:
                json.dump(from_backup, f, indent=4, cls=GenerationEncoder)
            for i in from_backup:
                self.not_revealed.append(i["item"])
            with open("src/Json/not_revealed.json", "w") as f:
                json.dump(self.not_revealed, f, indent=4)
            with open("src/Json/revealed.json", "w") as f:
                json.dump([], f)
            return
        elif filename in self.file_blacklist:
            raise ValueError(f"Cannot load backup with names {self.file_blacklist}!")
        else:
            raise FileNotFoundError(f"Backup {filename} does not exist!")
    
    def list(self):
        backups = [backup[:-5] for backup in os.listdir(self.directory) if backup.endswith(self.file_type) and backup not in self.file_blacklist]
        for backup in backups:
            self.backup_list += f"{backup} \n"
        return self.backup_list
    
    def remove(self, filename):
        backups = [backup[:-5] for backup in os.listdir(self.directory) if backup.endswith(self.file_type) and backup not in self.file_blacklist]
        if filename in backups:
            os.remove(f"src/Json/{filename}.json")
            return True
        elif filename in self.file_blacklist:
            raise ValueError(f"Cannot remove backup with names {self.file_blacklist}!")
        else:
            raise FileNotFoundError(f"Backup {filename} does not exist!")