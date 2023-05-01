import json
import random



class Reveal:
    def __init__(self):
        self.embed_description = ""
        try:
            with open("src/Json/generated.json", "r") as f:
                self.generated = json.load(f)
            with open("src/Json/not_revealed.json", "r") as f:
                self.not_revealed: list = json.load(f)
        except:
            self.error = "Must generate items first!"
        try:
            with open("src/Json/revealed.json", "r") as f:
                self.revealed: list = json.load(f)
        except:
            self.error = "Nothing revealed yet!"
            
    def tile(self):
        if len(self.not_revealed) > 0:
            to_reveal = random.sample(self.not_revealed, k=1)
            self.revealed.append(to_reveal[0])
            self.not_revealed.remove(to_reveal[0])
            with open("src/Json/not_revealed.json", "w") as f:
                json.dump(self.not_revealed, f, indent=4)
            with open("src/Json/revealed.json", "w") as f:
                json.dump(self.revealed, f, indent=4)
            for item in self.revealed:
                self.embed_description += f"{str(item.title())}\n"
            return self.embed_description
        else:
            return False
    
    
    def board(self):
        for pair in self.generated:
            item = pair["item"]
            prize = pair["prize"]
            self.embed_description += (f"{str(item).title()} : {str(prize).title()}\n")
        return self.embed_description