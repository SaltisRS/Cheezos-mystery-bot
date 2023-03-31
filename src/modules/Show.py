import json







class Show:
    def __init__(self):
        with open("src/Json/prizes.json", "r") as f:
            self.prizes = json.load(f)
        with open("src/Json/items.json", "r") as f:
            self.items = json.load(f)
        try:
            with open("src/Json/generated.json", "r") as f:
                self.generated = json.load(f)
        except:
            return "Must generate items first."
        try:
            with open("src/Json/revealed.json", "r") as f:
                self.revealed = json.load(f)
        except:
            return "No items have been revealed yet."
        self.embed_description = ""
                
            
    def Prizes(self):
        for prize in self.prizes:
            self.embed_description += f"{prize} \n"
        return self.embed_description
    
    def Items(self):
        for item in self.items:
            self.embed_description += f"{item} \n"
        return self.embed_description
    
    def Generated(self):
        for pair in self.generated:
            item = pair["item"]
            prize = pair["prize"]
            self.embed_description += f"{str(item).title()} : {str(prize).title()}\n"
        return self.embed_description
    
    def Revealed(self):
        for item in self.revealed:
            self.embed_description += f"{item} \n"
        return self.embed_description