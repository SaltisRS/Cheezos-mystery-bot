import json
import random
from .Dclasses import Generation
from .GenerationEncoder import GenerationEncoder
from dataclasses import asdict



class PrizeSelector:
    def __init__(self):
        with open("src/Json/prizes.json", "r") as f:
            self.prizes = json.load(f)
        with open("src/Json/items.json", "r") as f:
            self.items = json.load(f)
        with open("src/Json/generated.json", "r") as f:
            self.current_items = json.load(f)
    
    def select_prize(self, prize):
        new_item = random.sample(self.items, k=1)[0]
        for item in self.current_items:
            while new_item == item["item"]:
                new_item = random.sample(self.items, k=1)[0]
        if prize in self.prizes:
            item_prize = Generation(item=new_item, prize=prize)
            new_items = self.current_items + [asdict(item_prize)]
            with open("src/Json/generated.json", "w") as f:
                json.dump(new_items, f, indent=4, cls=GenerationEncoder)
            with open("src/Json/not_revealed.json", "w") as f:
                json.dump([new_item] + [item["item"] for item in self.current_items], f, indent=4)
            return f"Added {prize} to board"
        else:
            return "Not a valid prize"
