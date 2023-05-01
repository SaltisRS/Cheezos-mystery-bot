import json
from .DataStructure import Generation
from .GenerationEncoder import GenerationEncoder
import random

class BingoGenerator:
    def __init__(self):
        with open("src/Json/prizes.json", "r") as f:
            self.prizes = json.load(f)
        with open("src/Json/items.json", "r") as f:
            self.items = json.load(f)
        self.generated_items = []
        self.only_items = []
            
    def generate(self, amount: int):
        rand_item = random.sample(self.items, k=amount)
        rand_prize = random.sample(self.prizes, k=amount)
        for i in range(amount):
            self.generated_items.append(Generation(item=rand_item[i], prize=rand_prize[i]))
            self.only_items.append((rand_item[i]))
        with open("src/Json/not_revealed.json", "w") as f:
            json.dump(self.only_items, f, indent=4)
        with open("src/Json/generated.json", "w") as f:
            json.dump(self.generated_items, f, indent=4, cls=GenerationEncoder)
        with open("src/Json/revealed.json", "w") as f:
            json.dump([], f)
        return