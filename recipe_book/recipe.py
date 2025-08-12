from datetime import datetime
class Recipe:
    def __init__(self, name, ingredients,instructions,category,is_favorite:bool=False, created_at=None):
        self.name = name
        self.ingredients = ingredients #a list of dicts
        self.instructions = instructions
        self.category = category
        self.is_favorite = is_favorite
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def display(self):
        print(f"Recipe Name: {self.name}")
        print(f"Category: {self.category}")
        print(f"Ingredients:")
        for ingredient in self.ingredients:
            print(f" - {ingredient['amount']} {ingredient['name']}")
        print(f"Instructions: {self.instructions}")
        if self.is_favorite:
            print("⭐ This recipe is marked as a FAVORITE!")
        print(f"Created at: {self.created_at}")
