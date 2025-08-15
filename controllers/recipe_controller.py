# controllers/recipe_controller.py
import json
import csv
import os
from typing import List, Optional
from datetime import datetime
from collections import Counter

# Import models and utilities
from models.recipe import Recipe, RecipeCategory, Ingredient, NutritionalInfo
from services.recipe_service import RecipeService
from utils.console_utils import ConsoleManager, InteractiveMenu, InteractiveForm, FormField, Color

class RecipeController:
    def __init__(self, username: str):
        self.username = username
        self.service = RecipeService()
    
    def display_recipe(self, recipe: Recipe):
        """Display a single recipe with enhanced formatting"""
        print(f"\n{Color.CYAN}{Color.BOLD}{'='*60}{Color.RESET}")
        print(f"{Color.BOLD}📖 {recipe.name}{Color.RESET}")
        if recipe.is_favorite:
            print(f"{Color.YELLOW}⭐ FAVORITE{Color.RESET}")
        
        print(f"\n{Color.BLUE}Category:{Color.RESET} {recipe.category.value}")
        print(f"{Color.BLUE}Difficulty:{Color.RESET} {recipe.difficulty}")
        
        if recipe.prep_time or recipe.cook_time:
            times = []
            if recipe.prep_time:
                times.append(f"Prep: {recipe.prep_time}min")
            if recipe.cook_time:
                times.append(f"Cook: {recipe.cook_time}min")
            if recipe.total_time:
                times.append(f"Total: {recipe.total_time}min")
            print(f"{Color.BLUE}Time:{Color.RESET} {' | '.join(times)}")
        
        if recipe.servings:
            print(f"{Color.BLUE}Servings:{Color.RESET} {recipe.servings}")
        
        if recipe.rating:
            stars = "⭐" * int(recipe.rating)
            print(f"{Color.BLUE}Rating:{Color.RESET} {stars} ({recipe.rating}/5)")
        
        print(f"\n{Color.GREEN}{Color.BOLD}🛒 Ingredients:{Color.RESET}")
        for ingredient in recipe.ingredients:
            print(f"  • {ingredient}")
        
        print(f"\n{Color.PURPLE}{Color.BOLD}👨‍🍳 Instructions:{Color.RESET}")
        for i, instruction in enumerate(recipe.instructions, 1):
            print(f"  {i}. {instruction}")
        
        if recipe.tags:
            print(f"\n{Color.CYAN}🏷️ Tags:{Color.RESET} {', '.join(recipe.tags)}")
        
        if recipe.notes:
            print(f"\n{Color.YELLOW}📝 Notes:{Color.RESET} {recipe.notes}")
        
        if recipe.nutritional_info and any(vars(recipe.nutritional_info).values()):
            print(f"\n{Color.GREEN}🥗 Nutritional Info:{Color.RESET}")
            nutrition = recipe.nutritional_info
            if nutrition.calories:
                print(f"  Calories: {nutrition.calories}")
            if nutrition.protein:
                print(f"  Protein: {nutrition.protein}g")
            if nutrition.carbs:
                print(f"  Carbs: {nutrition.carbs}g")
            if nutrition.fat:
                print(f"  Fat: {nutrition.fat}g")
        
        print(f"\n{Color.BLUE}📅 Created:{Color.RESET} {recipe.created_at}")
        if recipe.updated_at != recipe.created_at:
            print(f"{Color.BLUE}📝 Updated:{Color.RESET} {recipe.updated_at}")
        
        print(f"{Color.CYAN}{'='*60}{Color.RESET}\n")
    
    def add_recipe(self):
        """Add a new recipe with interactive form"""
        fields = [
            FormField("name", "Recipe Name", required=True),
            FormField("category", "Category", "select", True, 
                     [cat.value for cat in RecipeCategory]),
            FormField("difficulty", "Difficulty Level", "select", True,
                     ["Easy", "Medium", "Hard"]),
            FormField("prep_time", "Preparation Time (minutes)", "number", False),
            FormField("cook_time", "Cooking Time (minutes)", "number", False),
            FormField("servings", "Number of Servings", "number", False),
            FormField("is_favorite", "Mark as Favorite?", "boolean", False),
        ]
        
        form = InteractiveForm("Add New Recipe - Basic Info", fields)
        basic_data = form.run()
        
        # Get ingredients
        ingredients = self._get_ingredients()
        if not ingredients:
            ConsoleManager.print_error("At least one ingredient is required!")
            return
        
        # Get instructions
        instructions = self._get_instructions()
        if not instructions:
            ConsoleManager.print_error("Instructions are required!")
            return
        
        # Optional fields
        tags = self._get_tags()
        notes = input(f"\n{Color.BLUE}Additional Notes (optional):{Color.RESET} ").strip()
        
        # Create recipe
        recipe = Recipe(
            name=basic_data["name"],
            ingredients=ingredients,
            instructions=instructions,
            category=RecipeCategory(basic_data["category"]),
            is_favorite=basic_data.get("is_favorite", False),
            prep_time=basic_data.get("prep_time"),
            cook_time=basic_data.get("cook_time"),
            servings=basic_data.get("servings"),
            difficulty=basic_data["difficulty"],
            tags=tags,
            notes=notes
        )
        
        if self.service.add_recipe(self.username, recipe):
            ConsoleManager.print_success(f"Recipe '{recipe.name}' added successfully!")
        else:
            ConsoleManager.print_error("Failed to add recipe!")
    
    def _get_ingredients(self) -> List[Ingredient]:
        """Interactive ingredient collection"""
        ingredients = []
        print(f"\n{Color.GREEN}🛒 Add Ingredients (press Enter with empty name to finish):{Color.RESET}")
        
        while True:
            print(f"\n{Color.BLUE}Ingredient #{len(ingredients) + 1}:{Color.RESET}")
            name = input("  Name: ").strip().title()
            if not name:
                break
            
            amount = input("  Amount: ").strip()
            if not amount:
                amount = "1"
            
            unit = input("  Unit (optional): ").strip()
            
            ingredients.append(Ingredient(name=name, amount=amount, unit=unit))
            print(f"  ✅ Added: {ingredients[-1]}")
        
        return ingredients
    
    def _get_instructions(self) -> List[str]:
        """Interactive instruction collection"""
        instructions = []
        print(f"\n{Color.PURPLE}👨‍🍳 Add Instructions (press Enter with empty instruction to finish):{Color.RESET}")
        
        while True:
            instruction = input(f"  Step {len(instructions) + 1}: ").strip()
            if not instruction:
                break
            instructions.append(instruction)
        
        return instructions
    
    def _get_tags(self) -> List[str]:
        """Get recipe tags"""
        print(f"\n{Color.CYAN}🏷️ Add Tags (comma-separated, optional):{Color.RESET}")
        tags_input = input("  Tags: ").strip()
        if tags_input:
            return [tag.strip().title() for tag in tags_input.split(",") if tag.strip()]
        return []
    
    def list_recipes(self):
        """Display all recipes with interactive selection"""
        recipes = self.service.load_recipes(self.username)
        if not recipes:
            ConsoleManager.print_warning("No recipes found!")
            return
        
        recipe_names = [f"{recipe.name} ({recipe.category.value})" for recipe in recipes]
        menu = InteractiveMenu("All Recipes", recipe_names)
        
        selected = menu.run()
        if selected >= 0 and selected < len(recipes):
            self.display_recipe(recipes[selected])
            self._recipe_actions_menu(recipes[selected])
    
    def _recipe_actions_menu(self, recipe: Recipe):
        """Show actions menu for a specific recipe"""
        actions = [
            "Edit Recipe",
            "Delete Recipe",
            "Toggle Favorite",
            "Rate Recipe"
        ]
        
        menu = InteractiveMenu(f"Actions for '{recipe.name}'", actions)
        selected = menu.run()
        
        if selected == 0:  # Edit
            self.edit_recipe(recipe.recipe_id)
        elif selected == 1:  # Delete
            self.delete_recipe(recipe.recipe_id)
        elif selected == 2:  # Toggle favorite
            self.toggle_favorite(recipe.recipe_id)
        elif selected == 3:  # Rate
            self.rate_recipe(recipe.recipe_id)
    
    def search_recipes(self):
        """Search recipes with enhanced interface"""
        query = input(f"\n{Color.BLUE}🔍 Enter search term:{Color.RESET} ").strip()
        if not query:
            ConsoleManager.print_warning("Search term cannot be empty!")
            return
        
        results = self.service.search_recipes(self.username, query)
        if not results:
            ConsoleManager.print_warning(f"No recipes found for '{query}'!")
            return
        
        ConsoleManager.print_success(f"Found {len(results)} recipe(s):")
        for i, recipe in enumerate(results, 1):
            print(f"\n{i}. {Color.BOLD}{recipe.name}{Color.RESET} ({recipe.category.value})")
            if recipe.is_favorite:
                print(f"   ⭐ Favorite")
        
        try:
            choice = int(input(f"\n{Color.BLUE}Select recipe to view (0 to cancel):{Color.RESET} "))
            if 1 <= choice <= len(results):
                self.display_recipe(results[choice - 1])
                self._recipe_actions_menu(results[choice - 1])
        except ValueError:
            ConsoleManager.print_error("Invalid selection!")
    
    def show_favorites(self):
        """Display favorite recipes"""
        favorites = self.service.get_favorites(self.username)
        if not favorites:
            ConsoleManager.print_warning("No favorite recipes found!")
            return
        
        recipe_names = [f"{recipe.name} ({recipe.category.value})" for recipe in favorites]
        menu = InteractiveMenu("⭐ Favorite Recipes", recipe_names)
        
        selected = menu.run()
        if selected >= 0 and selected < len(favorites):
            self.display_recipe(favorites[selected])
            self._recipe_actions_menu(favorites[selected])
    
    def browse_by_category(self):
        """Browse recipes by category"""
        categories = [cat.value for cat in RecipeCategory]
        menu = InteractiveMenu("Browse by Category", categories)
        
        selected = menu.run()
        if selected >= 0 and selected < len(categories):
            category = list(RecipeCategory)[selected]
            recipes = self.service.get_by_category(self.username, category)
            
            if not recipes:
                ConsoleManager.print_warning(f"No recipes found in {category.value} category!")
                return
            
            recipe_names = [recipe.name for recipe in recipes]
            recipe_menu = InteractiveMenu(f"{category.value} Recipes", recipe_names)
            
            recipe_selected = recipe_menu.run()
            if recipe_selected >= 0 and recipe_selected < len(recipes):
                self.display_recipe(recipes[recipe_selected])
                self._recipe_actions_menu(recipes[recipe_selected])
    
    def select_and_edit(self):
        """Select and edit a recipe"""
        recipes = self.service.load_recipes(self.username)
        if not recipes:
            ConsoleManager.print_warning("No recipes to edit!")
            return
        
        recipe_names = [recipe.name for recipe in recipes]
        menu = InteractiveMenu("Select Recipe to Edit", recipe_names)
        
        selected = menu.run()
        if selected >= 0 and selected < len(recipes):
            self.edit_recipe(recipes[selected].recipe_id)
    
    def select_and_delete(self):
        """Select and delete a recipe"""
        recipes = self.service.load_recipes(self.username)
        if not recipes:
            ConsoleManager.print_warning("No recipes to delete!")
            return
        
        recipe_names = [recipe.name for recipe in recipes]
        menu = InteractiveMenu("Select Recipe to Delete", recipe_names)
        
        selected = menu.run()
        if selected >= 0 and selected < len(recipes):
            self.delete_recipe(recipes[selected].recipe_id)
    
    def edit_recipe(self, recipe_id: str):
        """Edit an existing recipe"""
        recipes = self.service.load_recipes(self.username)
        recipe = next((r for r in recipes if r.recipe_id == recipe_id), None)
        
        if not recipe:
            ConsoleManager.print_error("Recipe not found!")
            return
        
        # Create form with current values
        fields = [
            FormField("name", "Recipe Name", required=True),
            FormField("category", "Category", "select", True, 
                     [cat.value for cat in RecipeCategory]),
            FormField("difficulty", "Difficulty Level", "select", True,
                     ["Easy", "Medium", "Hard"]),
            FormField("prep_time", "Preparation Time (minutes)", "number", False),
            FormField("cook_time", "Cooking Time (minutes)", "number", False),
            FormField("servings", "Number of Servings", "number", False),
        ]
        
        # Set current values
        for field in fields:
            if field.name == "name":
                field.value = recipe.name
            elif field.name == "category":
                field.value = recipe.category.value
            elif field.name == "difficulty":
                field.value = recipe.difficulty
            elif field.name == "prep_time":
                field.value = recipe.prep_time
            elif field.name == "cook_time":
                field.value = recipe.cook_time
            elif field.name == "servings":
                field.value = recipe.servings
        
        form = InteractiveForm(f"Edit Recipe - {recipe.name}", fields)
        updated_data = form.run()
        
        # Update recipe
        recipe.name = updated_data["name"]
        recipe.category = RecipeCategory(updated_data["category"])
        recipe.difficulty = updated_data["difficulty"]
        recipe.prep_time = updated_data.get("prep_time")
        recipe.cook_time = updated_data.get("cook_time")
        recipe.servings = updated_data.get("servings")
        
        if self.service.update_recipe(self.username, recipe_id, recipe):
            ConsoleManager.print_success("Recipe updated successfully!")
        else:
            ConsoleManager.print_error("Failed to update recipe!")
    
    def delete_recipe(self, recipe_id: str):
        """Delete a recipe with confirmation"""
        recipes = self.service.load_recipes(self.username)
        recipe = next((r for r in recipes if r.recipe_id == recipe_id), None)
        
        if not recipe:
            ConsoleManager.print_error("Recipe not found!")
            return
        
        ConsoleManager.print_warning(f"Delete recipe '{recipe.name}'?")
        menu = InteractiveMenu("Confirm Delete", ["Yes, Delete", "No, Cancel"])
        
        if menu.run() == 0:
            if self.service.delete_recipe(self.username, recipe_id):
                ConsoleManager.print_success(f"Recipe '{recipe.name}' deleted!")
            else:
                ConsoleManager.print_error("Failed to delete recipe!")
    
    def toggle_favorite(self, recipe_id: str):
        """Toggle favorite status of a recipe"""
        recipes = self.service.load_recipes(self.username)
        recipe = next((r for r in recipes if r.recipe_id == recipe_id), None)
        
        if recipe:
            recipe.is_favorite = not recipe.is_favorite
            if self.service.update_recipe(self.username, recipe_id, recipe):
                status = "added to" if recipe.is_favorite else "removed from"
                ConsoleManager.print_success(f"Recipe {status} favorites!")
    
    def rate_recipe(self, recipe_id: str):
        """Rate a recipe"""
        recipes = self.service.load_recipes(self.username)
        recipe = next((r for r in recipes if r.recipe_id == recipe_id), None)
        
        if recipe:
            rating_options = ["⭐ (1)", "⭐⭐ (2)", "⭐⭐⭐ (3)", "⭐⭐⭐⭐ (4)", "⭐⭐⭐⭐⭐ (5)"]
            menu = InteractiveMenu("Rate Recipe", rating_options)
            
            selected = menu.run()
            if selected >= 0:
                recipe.rating = selected + 1
                if self.service.update_recipe(self.username, recipe_id, recipe):
                    ConsoleManager.print_success(f"Recipe rated {recipe.rating}/5 stars!")
    
    def show_statistics(self):
        """Display comprehensive recipe statistics"""
        stats = self.service.get_statistics(self.username)
        
        ConsoleManager.clear_screen()
        ConsoleManager.print_header("📊 Recipe Statistics")
        
        print(f"\n{Color.GREEN}📚 Total Recipes:{Color.RESET} {stats['total_recipes']}")
        print(f"{Color.YELLOW}⭐ Favorites:{Color.RESET} {stats['total_favorites']}")
        
        if stats['avg_rating'] > 0:
            print(f"{Color.BLUE}📈 Average Rating:{Color.RESET} {stats['avg_rating']:.1f}/5")
        
        if stats['categories']:
            print(f"\n{Color.PURPLE}🍽️ Recipes by Category:{Color.RESET}")
            for category, count in stats['categories'].items():
                print(f"  • {category}: {count}")
        
        if stats['difficulties']:
            print(f"\n{Color.CYAN}🎯 Difficulty Distribution:{Color.RESET}")
            for difficulty, count in stats['difficulties'].items():
                print(f"  • {difficulty}: {count}")
        
        input(f"\n{Color.YELLOW}Press Enter to continue...{Color.RESET}")
    
    def export_recipes(self, format_choice: int, filename: str) -> bool:
        """Export recipes in various formats"""
        recipes = self.service.load_recipes(self.username)
        if not recipes:
            return False
        
        try:
            if format_choice == 0:  # JSON
                with open(f"{filename}.json", 'w', encoding='utf-8') as f:
                    json.dump([recipe.to_dict() for recipe in recipes], f, indent=2)
            elif format_choice == 1:  # Text
                with open(f"{filename}.txt", 'w', encoding='utf-8') as f:
                    for recipe in recipes:
                        f.write(f"Recipe: {recipe.name}\n")
                        f.write(f"Category: {recipe.category.value}\n")
                        f.write(f"Ingredients:\n")
                        for ing in recipe.ingredients:
                            f.write(f"  - {ing}\n")
                        f.write(f"Instructions:\n")
                        for i, inst in enumerate(recipe.instructions, 1):
                            f.write(f"  {i}. {inst}\n")
                        f.write("\n" + "="*50 + "\n\n")
            elif format_choice == 2:  # CSV
                with open(f"{filename}.csv", 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Name', 'Category', 'Ingredients', 'Instructions', 'Favorite'])
                    for recipe in recipes:
                        ingredients_str = '; '.join(str(ing) for ing in recipe.ingredients)
                        instructions_str = '; '.join(recipe.instructions)
                        writer.writerow([recipe.name, recipe.category.value, 
                                       ingredients_str, instructions_str, recipe.is_favorite])
            return True
        except Exception as e:
            ConsoleManager.print_error(f"Export error: {e}")
            return False
    
    def import_recipes(self, filename: str) -> bool:
        """Import recipes from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                imported_recipes = [Recipe.from_dict(recipe_data) for recipe_data in data]
                
                current_recipes = self.service.load_recipes(self.username)
                current_recipes.extend(imported_recipes)
                
                return self.service.save_recipes(self.username, current_recipes)
        except Exception as e:
            ConsoleManager.print_error(f"Import error: {e}")
            return False
    
    def create_backup(self) -> bool:
        """Create a backup of user recipes"""
        backup_filename = f"backup_{self.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return self.export_recipes(0, backup_filename)
    
    def show_advanced_statistics(self):
        """Show advanced recipe statistics and analytics"""
        recipes = self.service.load_recipes(self.username)
        if not recipes:
            ConsoleManager.print_warning("No recipes for analysis!")
            return
        
        ConsoleManager.clear_screen()
        ConsoleManager.print_header("📈 Advanced Recipe Analytics")
        
        # Time-based analysis
        total_prep_time = sum(r.prep_time for r in recipes if r.prep_time)
        total_cook_time = sum(r.cook_time for r in recipes if r.cook_time)
        avg_prep_time = total_prep_time / len([r for r in recipes if r.prep_time]) if any(r.prep_time for r in recipes) else 0
        avg_cook_time = total_cook_time / len([r for r in recipes if r.cook_time]) if any(r.cook_time for r in recipes) else 0
        
        print(f"\n{Color.BLUE}⏱️ Time Analysis:{Color.RESET}")
        print(f"  Total Prep Time: {total_prep_time} minutes")
        print(f"  Total Cook Time: {total_cook_time} minutes")
        print(f"  Average Prep Time: {avg_prep_time:.1f} minutes")
        print(f"  Average Cook Time: {avg_cook_time:.1f} minutes")
        
        # Ingredient analysis
        all_ingredients = []
        for recipe in recipes:
            all_ingredients.extend([ing.name.lower() for ing in recipe.ingredients])
        
        ingredient_counts = Counter(all_ingredients)
        most_common = ingredient_counts.most_common(5)
        
        print(f"\n{Color.GREEN}🥗 Most Used Ingredients:{Color.RESET}")
        for ingredient, count in most_common:
            print(f"  • {ingredient.title()}: {count} recipes")
        
        # Rating analysis
        rated_recipes = [r for r in recipes if r.rating]
        if rated_recipes:
            avg_rating = sum(r.rating for r in rated_recipes) / len(rated_recipes)
            highest_rated = max(rated_recipes, key=lambda r: r.rating)
            
            print(f"\n{Color.YELLOW}⭐ Rating Analysis:{Color.RESET}")
            print(f"  Average Rating: {avg_rating:.1f}/5")
            print(f"  Highest Rated: {highest_rated.name} ({highest_rated.rating}/5)")
            print(f"  Rated Recipes: {len(rated_recipes)}/{len(recipes)}")
        
        # Recipe creation timeline
        created_dates = [datetime.fromisoformat(r.created_at).date() for r in recipes]
        date_counts = Counter(created_dates)
        
        print(f"\n{Color.PURPLE}📅 Creation Timeline:{Color.RESET}")
        print(f"  Most Productive Day: {max(date_counts, key=date_counts.get)} ({max(date_counts.values())} recipes)")
        print(f"  Recipe Creation Span: {min(created_dates)} to {max(created_dates)}")
        
        input(f"\n{Color.YELLOW}Press Enter to continue...{Color.RESET}")