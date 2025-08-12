from recipe import Recipe
import os
import json
from datetime import datetime

def read_json(filename):
    if not os.path.exists(filename):
        return[]
    try:
        with open(filename,"r",encoding="utf-8") as file:
            data=json.load(file)
            return[Recipe(**r) for r in data] #**r turns the dicts directly into a Recipe object
    except json.decoder.JSONDecodeError:
        print("❌ Error: Recipe file is corrupted or not valid JSON.")
        return []
    except Exception as e:
        print(f"🚨 Unexpected error reading '{filename}': {e}")
        return []

def login():
    print("📔 Welcome to the Recipe Book! 😊\n")
    while True:
        has_account=input("❓ Do you already have account? (y/n): ").strip().lower()
        if has_account in("y","n"):
            break
        print("Please enter 'y' or 'n': ")

    if has_account == "y":
        while True:
            username=input("👥 Enter your username: ").strip().lower()
            if not username:
                print("❌ Username cannot be empty.")
                continue
            if " " in username :
                print("❌ Username cannot contain spaces.")
            if not username.isalnum():
                print("❌ Username must contain only letters and numbers.")
                continue
            break
        filename=f"user_recipes/recipes_{username}.json"
        if os.path.exists(filename):
            print(f"🤗 Welcome back, {username}!\n")
            return filename
        else:
            print("Sorry, no such user found. Please try again!")
            return login()
    elif has_account == "n":
        while True:
            while True:
                username=input("👥 Create a username: ").strip().lower()
                if not username:
                    print("❌ Username cannot be empty.")
                    continue
                if " " in username:
                    print("❌ Username cannot contain spaces.")
                if not username.isalnum():
                    print("❌ Username must contain only letters and numbers.")
                    continue
                break
            filename=f"user_recipes/recipes_{username}.json"
            if os.path.exists(filename):
                print("🚫 This username already exists! Please choose another one.")
            else:
                print(f"✅ Account created for {username}! Welcome! 🤗")
                with open(filename,"w",encoding="utf-8") as file:
                    file.write("[]") #empty json just to add the user
                return filename
    else:
        print("🚫 Invalid input! Please enter 'y' for existing or 'n' for new user.")
        return login()

def save_to_json(filename,recipes):
    with open(filename,"w",encoding="utf-8") as file:
        json.dump([r.__dict__ for r in recipes],file,ensure_ascii=False,indent=4) #turns recipe list objects into dict


def add_recipe(filename):
    recipes=read_json(filename)
    #new recipe info
    while True:
        name=input("📝 Enter recipe name: ").title()
        if name:
            break
        elif name=="0" or name.lower()=="menu":
            print("↩️ Returning to main menu...")
            return
        print("🚨 Recipe name cannot be empty!")

    while True:
        category=input("📝 Enter category: ").title()
        if category:
            break
        elif category=="0" or category.lower()=="menu":
            print("↩️ Returning to main menu...")
            return
        print("🚨 Category cannot be empty!")

    #ingredients info
    ingredients=[]
    print("📝 Enter ingredients (leave name empty to stop):")
    while True:
        ing_name=input(" - Ingredient name: ").strip().capitalize()
        if ing_name == "0" or ing_name.lower() == "menu":
            print("↩️ Returning to main menu...")
            return
        if not ing_name:
            if ingredients:
                break

            else:
                print("🚨 You must enter at least one ingredient!")
                continue
        while True:
            amount=input(" - Amount (e.g 2 tablespoon): ").strip()
            if amount == "0" or amount.lower() == "menu":
                print("↩️ Returning to main menu...")
                return
            if amount:
                break
            print("🚨 Amount cannot be empty!")
        ingredients.append({
                "name": ing_name,
                "amount": amount,
            })
    while True:
        instructions=input("📝 Enter instructions: ").capitalize()
        if instructions:
            break
        elif instructions=="0" or instructions.lower()=="menu":
            print("↩️ Returning to main menu...")
            return
        print("🚨 Instructions cannot be empty!")

    #to add it as fav or not
    while True:
        fav=input("⭐ Mark this as your favorite? (y/n or blank to skip): ").strip().lower()
        if fav=="0" or fav.lower()=="menu":
            print("↩️ Returning to main menu...")
            return
        if fav in ("y", "n",""):
            break

        print("🚨 Invalid input! Must be 'y' or 'n'.")

    is_favorite= True if fav == "y" else False

    #create new recipe object
    recipe=Recipe(name,ingredients,instructions,category,is_favorite)
    try:
        recipes.append(recipe)
        save_to_json(filename,recipes)
        print(f"✅ New recipe added: {name}")
    except Exception as e:
        print(f"🚨 Error adding recipe: {e}")


def display_recipes(filename):
    recipes = read_json(filename)
    if not recipes or recipes==['']:
        print("⚠️ No recipes found!")
        return
    print("\n📒 All Recipes:\n")
    for i,recipe in enumerate(recipes, start=1): # takes recipe object from recipes list
        print(f"Recipe #{i}:")
        recipe.display() #uses the display function from the class
        print("\n" + "*" * 30 + "\n")

def delete_recipe(filename):
    recipes=read_json(filename)
    if not recipes:
        print("⚠️ No recipes found.")
        return
    while True:
        name_to_delete=input("📝 Enter the name of the recipe you want to delete: ")
        if name_to_delete=="0" or name_to_delete.lower()=="menu":
            print("↩️ Returning to main menu...")
            return
        if name_to_delete:
            break

        print("❌ Recipe name cannot be empty.")

    updated_recipes=[]
    found=False

    for recipe in recipes:
        if recipe.name.lower()==name_to_delete.lower():
            found=True
            print(f"🚮Recipe {recipe.name} deleted successfully!")
        else:
            updated_recipes.append(recipe)
    if found:
        try:
            save_to_json(filename,updated_recipes)
            print(f"✅ Recipe '{name_to_delete}' has been deleted.")
        except Exception as e:
            print(f"🚨 Error saving updated file: {e}")
    else:
        print(f"🚫Recipe {name_to_delete} not found!")
        return delete_recipe(filename)

def edit_recipe(filename):
    recipes = read_json(filename)
    if not recipes:
        print("⚠️ No recipes found.")
        return
    while True:
        name_to_edit=input("📝Enter the name of the recipe you want to edit: ").strip().lower()
        if name_to_edit=="0" or name_to_edit.lower()=="menu":
            print("↩️ Returning to main menu...")
            return
        if name_to_edit:
            break

        print("⚠️ Recipe name cannot be empty!")

    updated_recipes=[]
    found=False
    if not recipes:
        print("⚠️ No recipes found!")
        return

    for recipe in recipes:
        if recipe.name.lower()==name_to_edit.lower():
            found=True
            print(f"📑Editing Recipe: {recipe.name}")
            print("Leave the input blank if you want to keep the current value.")

            new_name=input(f"📝 Enter new recipe name: [{recipe.name}]: ").strip().title()
            if new_name=="0" or new_name.lower()=="menu":
                print("↩️ Returning to main menu...")
                return
            new_instructions=input(f"📝 Enter new instructions [{recipe.instructions}]: ").strip().capitalize()
            if new_instructions=="0" or new_instructions.lower()=="menu":
                print("↩️ Returning to main menu...")
                return
            new_category=input(f"📝 Enter new category [{recipe.category}]: ").strip().title()
            if new_category=="0" or new_category.lower()=="menu":
                print("↩️ Returning to main menu...")
                return
            while True:
                fav=input("⭐❓ Update favorite status? (y/n or blank to skip): ").strip().lower()
                if fav == "0" or fav == "menu":
                    print("↩️ Returning to main menu...")
                    return
                if fav in("y","n",""):
                    break

                print("⚠️ Invalid input! Must be 'y' or 'n'.")
            if fav=="y":
                recipe.is_favorite=True
            elif fav=="n":
                recipe.is_favorite=False
            print("\n📑 Updating ingredients:")
            for i,ing in enumerate(recipe.ingredients):
                print(f"Ingredient #{i+1}: {ing['amount']} {ing['name']}")
                new_ing_name=input(" New name: ").strip().capitalize()
                if new_ing_name=="0" or new_ing_name.lower()=="menu":
                    print("↩️ Returning to main menu...")
                    return
                if new_ing_name:
                    ing['name'] = new_ing_name
                while True:
                    new_ing_amount=input(" New amount: ").strip()
                    if new_ing_amount=="0" or new_ing_amount.lower()=="menu":
                        print("↩️ Returning to main menu...")
                        return
                    if new_ing_amount:
                        ing['amount'] = new_ing_amount
                        break
                    elif not new_ing_name: #if name also didnt change break
                        break
                    else:
                        print("❌ Amount cannot be empty if name is changed.")

                if new_ing_name:
                    ing['name'] = new_ing_name
                if new_ing_amount:
                    ing['amount'] = new_ing_amount

            recipe.name=new_name if new_name else recipe.name #keep the original value if blank
            recipe.instructions=new_instructions if new_instructions else recipe.instructions
            recipe.category=new_category if new_category else recipe.category

        updated_recipes.append(recipe)
    if found:
        try:
            save_to_json(filename,updated_recipes)
            print(f"✅ Recipe {name_to_edit} edited successfully!")
        except Exception as e:
            print(f"🚨 Error saving updated recipe: {e}")
    else:
        print(f"🚫 Recipe {name_to_edit} not found!")
        return edit_recipe(filename)


def search_recipe(filename):
    recipes = read_json(filename)
    if not recipes:
        print("⚠️ No recipes found.")
        return

    while True:
        keyword=input("📝 Enter the search keyword (name/ingredients/instructions): ").strip().lower()
        if keyword=="0" or keyword.lower()=="menu":
            print("↩️ Returning to main menu...")
            return
        if keyword and len(keyword)>=2:
            break

        print("⚠️ Search keyword cannot be empty and must be at least 2 characters long.")
    found=False
    for recipe in recipes:
        ingredient_names=[ing['name'].lower() for ing in recipe.ingredients]
        if(
                keyword in recipe.name.lower()
                or keyword in recipe.instructions.lower()
                or any(keyword in ing_name for ing_name in ingredient_names)
        ):
            print("\n🔎 Match found:")
            recipe.display() #call display function from class
            print("\n" + "*" * 30 + "\n")
            found=True
    if not found:
        print(f"❌ No relevant recipe found for {keyword}!")
        return search_recipe(filename)

def fav_recipes(filename):
    recipes=read_json(filename)
    favorites=list(filter(lambda recipe: recipe.is_favorite, recipes))
    if not favorites:
        print("❌ No favorites found!")
        return
    print("\n⭐ Favorites Recipes:")
    list(map(lambda recipe: (recipe.display(), print("\n" + "*"*30)), favorites))

def show_statistics(filename):
    recipes=read_json(filename)
    total=len(recipes)
    if total==0:
        print("❌ No recipes exists!")
        return

    # for fav recipes
    fav_count=len(list(filter(lambda recipe: recipe.is_favorite, recipes)))

    #for categories
    categories=list(map(lambda recipe: recipe.category, recipes))
    distinct_categories=set(categories)

    print("\n📊 Recipe Statistics")
    print("📚 Total Recipes: ", total)
    print("⭐ Total Favorites: ", fav_count)
    print(f"🍴 Categories: {len(distinct_categories)} ({"-".join(distinct_categories)})")

def filter_by_category(filename):
    recipes=read_json(filename)

    if not recipes:
        print("⚠️ No recipes found.")
        return
    while True:
        category=input("📝 Enter the category to filter (e.g dessert/main/soup): ").strip().lower()
        if category:
            break
        elif category=="0" or category=="menu":
            print("↩️ Returning to main menu...")
            return
        print("❌ Category cannot be empty.")

    matches=list(filter(lambda r:r.category.lower()==category,recipes))
    if not matches:
        print(f"\n❌ No recipes found in the category '{category}'.")
        return
    print(f"\n📂 Recipes in category: {category.capitalize()}\n")
    for i,recipe in enumerate(matches,1):
        print(f"Recipe #{i}")
        recipe.display()
        print("\n" + "*" * 30)

def latest_recipe(filename):
    recipes=read_json(filename)
    if recipes:
        recent=max(
            recipes,key=lambda recipe: datetime.strptime(recipe.created_at, "%Y-%m-%d %H:%M:%S")
        )
        print("🕓 Most recently added recipe:")
        recent.display()
    else:
        print("❌ No recipes to analyze.")