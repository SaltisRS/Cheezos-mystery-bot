import json
from .GenerationEncoder import GenerationEncoder



class Verify:
    """
    Handles updating related files and running a check against the generated items file.
    """
    def __init__(self) -> None:

        self.generated = []
        self.prizes = []
        self.not_revealed = []
        
        with open("src/Json/generated.json", "r") as f:
            self.generated = json.load(f)
        with open("src/Json/prizes.json", "r") as f:
            self.prizes = json.load(f)
        with open("src/Json/not_revealed.json") as f:
            self.not_revealed = json.load(f)


    def verify_drop(self, item: str) -> tuple | bool:
        for pair in self.generated:
            if item == pair["item"]:
                print(f"Found pair: {pair}")
                self.remove_pair(pair=pair)
                self.remove_prize(prize=pair["prize"])
                self.remove_not_revealed(item=item)
                return pair
        return False

            
    def remove_pair(self, pair) -> None:
        self.generated.remove(pair)
        with open("src/Json/generated.json", "w") as f:
            json.dump(self.generated, f, indent=4, cls=GenerationEncoder)
            print(f"Removed won pair: {pair}")
        return
    
    def remove_prize(self, prize: str) -> None:
        try:
            self.prizes.remove(prize)
            with open("src/Json/prizes.json", "w") as f:
                json.dump(self.prizes, f, indent=4)
                print(f"Removed won prize: {prize}")
        except ValueError:
            print(f"Prize not found: {prize}")
        return
            
    def remove_not_revealed(self, item: str) -> None:
        try:
            self.not_revealed.remove(item)
            with open("src/Json/not_revealed.json", "w") as f:
                json.dump(self.not_revealed, f, indent=4)
                print(f"Updated removed item: {item}")
        except ValueError:
            print(f"Item not found: {item}")
        return