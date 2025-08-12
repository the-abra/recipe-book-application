from interactions import *

filename=login()
def call_menu():
      print(
            "Please choose an option:\n"
            "0) Return to Main Menu\n"
            "1) Add a new recipe\n"
            "2) Search for a recipe\n"
            "3) Edit a recipe\n"
            "4) Delete a recipe\n"
            "5) Display all recipes\n"
            "6) Show favorite recipes\n"
            "7) Show Recipe Statistics\n"
            "8) Filter by Category\n"
            "9) Latest Recipe\n"
            "10) Exit\n")
call_menu()


try:
      while True:
            choice = input("\nWhat would you like to do?: ")
            if choice == "0" or choice.lower()=="menu":
                  call_menu()
            elif choice=="1" or choice=="add":
                  add_recipe(filename)
            elif choice=="2" or choice=="search":
                  search_recipe(filename)
            elif choice=="3" or choice=="edit":
                  edit_recipe(filename)
            elif choice=="4" or choice=="delete":
                  delete_recipe(filename)
            elif choice=="5" or choice=="display":
                  display_recipes(filename)
            elif choice=="6" or choice=="favorite":
                  fav_recipes(filename)
            elif choice=="7" or choice=="statistics":
                  show_statistics(filename)
            elif choice=="8" or choice=="category":
                  filter_by_category(filename)
            elif choice=="9" or choice=="latest":
                  latest_recipe(filename)
            elif choice=="10" or choice=="exit":
                  print("👋 Goodbye!!")
                  break
            else:
                  print("Invalid choice, please select a number between 1 and 10 (0 to see the menu")
except Exception as e:
      print("🚨 An unexpected error occurred:",e)