# services/recipe_service.py
import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime

# Import models
from models.recipe import Recipe, RecipeCategory
from utils.console_utils import ConsoleManager

class RecipeService:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def get_user_file(self, username: str) -> str:
        return os.path.join(self.data_dir, f"recipes_{username}.json")
    
    def load_recipes(self, username: str) -> List[Recipe]:
        filename = self.get_user_file(username)
        if not os.path.exists(filename):
            return []
        
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return [Recipe.from_dict(recipe_data) for recipe_data in data]
        except json.JSONDecodeError:
            ConsoleManager.print_error("Recipe file is corrupted!")
            return []
        except Exception as e:
            ConsoleManager.print_error(f"Error loading recipes: {e}")
            return []
    
    def save_recipes(self, username: str, recipes: List[Recipe]) -> bool:
        filename = self.get_user_file(username)
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump([recipe.to_dict() for recipe in recipes], 
                         file, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            ConsoleManager.print_error(f"Error saving recipes: {e}")
            return False
    
    def create_user(self, username: str) -> bool:
        filename = self.get_user_file(username)
        if os.path.exists(filename):
            return False
        
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump([], file)
            return True
        except Exception as e:
            ConsoleManager.print_error(f"Error creating user: {e}")
            return False
    
    def user_exists(self, username: str) -> bool:
        return os.path.exists(self.get_user_file(username))
    
    def add_recipe(self, username: str, recipe: Recipe) -> bool:
        recipes = self.load_recipes(username)
        recipes.append(recipe)
        return self.save_recipes(username, recipes)
    
    def update_recipe(self, username: str, recipe_id: str, updated_recipe: Recipe) -> bool:
        recipes = self.load_recipes(username)
        for i, recipe in enumerate(recipes):
            if recipe.recipe_id == recipe_id:
                updated_recipe.updated_at = datetime.now().isoformat()
                recipes[i] = updated_recipe
                return self.save_recipes(username, recipes)
        return False
    
    def delete_recipe(self, username: str, recipe_id: str) -> bool:
        recipes = self.load_recipes(username)
        original_count = len(recipes)
        recipes = [r for r in recipes if r.recipe_id != recipe_id]
        if len(recipes) < original_count:
            return self.save_recipes(username, recipes)
        return False
    
    def search_recipes(self, username: str, query: str) -> List[Recipe]:
        recipes = self.load_recipes(username)
        query = query.lower()
        
        results = []
        for recipe in recipes:
            # Search in name, instructions, ingredients, and tags
            if (query in recipe.name.lower() or
                any(query in instruction.lower() for instruction in recipe.instructions) or
                any(query in ingredient.name.lower() for ingredient in recipe.ingredients) or
                any(query in tag.lower() for tag in recipe.tags)):
                results.append(recipe)
        
        return results
    
    def get_favorites(self, username: str) -> List[Recipe]:
        recipes = self.load_recipes(username)
        return [recipe for recipe in recipes if recipe.is_favorite]
    
    def get_by_category(self, username: str, category: RecipeCategory) -> List[Recipe]:
        recipes = self.load_recipes(username)
        return [recipe for recipe in recipes if recipe.category == category]
    
    def get_statistics(self, username: str) -> Dict[str, Any]:
        recipes = self.load_recipes(username)
        categories = {}
        total_favorites = 0
        difficulties = {}
        
        for recipe in recipes:
            # Category stats
            cat_name = recipe.category.value
            categories[cat_name] = categories.get(cat_name, 0) + 1
            
            # Favorites
            if recipe.is_favorite:
                total_favorites += 1
            
            # Difficulty stats
            difficulties[recipe.difficulty] = difficulties.get(recipe.difficulty, 0) + 1
        
        return {
            'total_recipes': len(recipes),
            'total_favorites': total_favorites,
            'categories': categories,
            'difficulties': difficulties,
            'avg_rating': sum(r.rating for r in recipes if r.rating) / len([r for r in recipes if r.rating]) if any(r.rating for r in recipes) else 0
        }