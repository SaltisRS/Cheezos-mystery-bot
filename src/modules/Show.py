import json

class Show:
    def __init__(self):
        with open("src/Json/prizes.json", "r") as f:
            self.prize = json.load(f)
        with open("src/Json/items.json", "r") as f:
            self.item = json.load(f)
        try:
            with open("src/Json/generated.json", "r") as f:
                self.gen = json.load(f)
        except Exception as e:
            print(e)
        try:
            with open("src/Json/revealed.json", "r") as f:
                self.reveal = json.load(f)
        except Exception as e:
            print(e)
        self.embed_description = ""
                
            
    def prizes(self):
        for prize in self.prize:
            self.embed_description += f"{prize} \n"
        return self.embed_description
    
    def items(self):
        for item in self.item:
            self.embed_description += f"{item} \n"
        return self.embed_description
    
    def generated(self):
        for pair in self.gen:
            item = pair["item"]
            prize = pair["prize"]
            self.embed_description += f"{str(item).title()} : {str(prize).title()}\n"
        return self.embed_description
    
    def revealed(self):
        for item in self.reveal:
            self.embed_description += f"{item} \n"
        return self.embed_description