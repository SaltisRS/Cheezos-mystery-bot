import json

class BingoHandler:
    def __init__(self):
        self.prizes = "src/Json/prizes.json"
        self.items = "src/Json/items.json"
        with open(self.prizes, "r") as f:
            self.prize_data = json.load(f)
        with open(self.items, "r") as f:
                self.item_data = json.load(f)
    
    def Additem(self, item):
        if item not in self.item_data:
            self.item_data.append(item)
            self.item_data.sort()
            with open(self.items, "w") as f:
                json.dump(self.item_data, f, indent=4)
            return
        else:
            return False
    
    def Addprize(self, prize):
        if prize not in self.prize_data:
            self.prize_data.append()
            self.prize_data.sort()
            with open(self.prizes, "w") as f:
                json.dump(self.prize_data, f, indent=4)
            return
        else:
            return False
    
    def Removeitem(self, item):
        if item in self.item_data:
            self.item_data.remove(item)
            self.item_data.sort()
            with open(self.items, "w") as f:
                json.dump(self.item_data, f, indent=4)
            return
        else:
            return False
    
    def Removeprize(self, prize):
        if prize in self.prize_data:
            self.prize_data.remove(prize)
            self.prize_data.sort()
            with open(self.prizes, "w") as f:
                json.dump(self.prize_data, f, indent=4)
            return
        else:
            return False
            