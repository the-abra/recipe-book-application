# main.py
import re
import os
from controllers.recipe_controller import RecipeController
from services.recipe_service import RecipeService
from utils.console_utils import ConsoleManager, InteractiveMenu, Color

class RecipeApp:
    def __init__(self):
        self.service = RecipeService()
        self.controller = None
        self.username = None
    
    def authenticate(self):
        """Handle user authentication with enhanced interface"""
        ConsoleManager.clear_screen()
        ConsoleManager.print_header("🍳 Professional Recipe Management System")
        
        menu = InteractiveMenu("Welcome", ["Login to Existing Account", "Create New Account"])
        choice = menu.run()
        
        if choice == -1:  # ESC pressed
            return False
        
        if choice == 0:  # Login
            return self._login()
        else:  # Create account
            return self._create_account()
    
    def _login(self):
        """Login to existing account"""
        while True:
            ConsoleManager.clear_screen()
            ConsoleManager.print_header("🔐 Login")
            
            username = input(f"\n{Color.BLUE}Username:{Color.RESET} ").strip().lower()
            if not username:
                ConsoleManager.print_error("Username cannot be empty!")
                input("Press Enter to continue...")
                continue
            
            if not self._validate_username(username):
                continue
            
            if not self.service.user_exists(username):
                ConsoleManager.print_error("User not found!")
                retry_menu = InteractiveMenu("User Not Found", ["Try Again", "Create New Account"])
                choice = retry_menu.run()
                if choice == 1:
                    return self._create_account()
                continue
            
            self.username = username
            self.controller = RecipeController(username)
            ConsoleManager.print_success(f"Welcome back, {username}!")
            input("Press Enter to continue...")
            return True
    
    def _create_account(self):
        """Create new user account"""
        while True:
            ConsoleManager.clear_screen()
            ConsoleManager.print_header("📝 Create Account")
            
            username = input(f"\n{Color.BLUE}Choose Username:{Color.RESET} ").strip().lower()
            if not username:
                ConsoleManager.print_error("Username cannot be empty!")
                input("Press Enter to continue...")
                continue
            
            if not self._validate_username(username):
                continue
            
            if self.service.user_exists(username):
                ConsoleManager.print_error("Username already exists!")
                input("Press Enter to continue...")
                continue
            
            if self.service.create_user(username):
                self.username = username
                self.controller = RecipeController(username)
                ConsoleManager.print_success(f"Account created successfully! Welcome, {username}!")
                input("Press Enter to continue...")
                return True
            else:
                ConsoleManager.print_error("Failed to create account!")
                input("Press Enter to continue...")
    
    def _validate_username(self, username: str) -> bool:
        """Validate username format"""
        if not re.match("^[a-zA-Z0-9_]{3,20}$", username):
            ConsoleManager.print_error("Username must be 3-20 characters, letters, numbers, and underscores only!")
            input("Press Enter to continue...")
            return False
        return True
    
    def run(self):
        """Main application loop"""
        # Display welcome message with interface info
        ConsoleManager.clear_screen()
        ConsoleManager.print_header("🍳 Professional Recipe Management System")
        
        # Detect and display interface mode
        test_menu = InteractiveMenu("", [], show_back=False)
        if test_menu.use_arrows:
            ConsoleManager.print_info("✅ Arrow key navigation enabled")
        else:
            ConsoleManager.print_info("📟 Using number selection mode (arrow keys not available)")
        
        print(f"\n{Color.YELLOW}Press Enter to continue...{Color.RESET}")
        input()
        
        if not self.authenticate():
            return
        
        while True:
            try:
                choice = self._main_menu()
                if choice == -1 or choice == 9:  # ESC or Exit
                    ConsoleManager.print_info("Thank you for using Recipe Management System!")
                    break
                
                self._handle_menu_choice(choice)
                
            except KeyboardInterrupt:
                print(f"\n{Color.YELLOW}Goodbye!{Color.RESET}")
                break
            except Exception as e:
                ConsoleManager.print_error(f"An error occurred: {e}")
                input("Press Enter to continue...")
    
    def _main_menu(self) -> int:
        """Display main menu and get user choice"""
        menu_options = [
            "🆕 Add New Recipe",
            "📋 View All Recipes", 
            "🔍 Search Recipes",
            "⭐ View Favorites",
            "🗂️ Browse by Category",
            "✏️ Edit Recipe",
            "🗑️ Delete Recipe",
            "📊 View Statistics",
            "⚙️ Settings",
            "🚪 Exit"
        ]
        
        menu = InteractiveMenu(f"Main Menu - Welcome {self.username}!", menu_options, show_back=False)
        return menu.run()
    
    def _handle_menu_choice(self, choice: int):
        """Handle main menu selections"""
        if choice == 0:  # Add Recipe
            self.controller.add_recipe()
        elif choice == 1:  # View All
            self.controller.list_recipes()
        elif choice == 2:  # Search
            self.controller.search_recipes()
        elif choice == 3:  # Favorites
            self.controller.show_favorites()
        elif choice == 4:  # Browse by Category
            self.controller.browse_by_category()
        elif choice == 5:  # Edit Recipe
            self.controller.select_and_edit()
        elif choice == 6:  # Delete Recipe
            self.controller.select_and_delete()
        elif choice == 7:  # Statistics
            self.controller.show_statistics()
        elif choice == 8:  # Settings
            self._settings_menu()
        
        if choice not in [7, 8]:  # Don't pause after statistics or settings
            input(f"\n{Color.YELLOW}Press Enter to continue...{Color.RESET}")
    
    def _settings_menu(self):
        """Settings and advanced options"""
        settings_options = [
            "📤 Export Recipes",
            "📥 Import Recipes", 
            "🔄 Backup Data",
            "🗑️ Delete All Recipes",
            "👤 Change Username",
            "📈 Advanced Statistics"
        ]
        
        menu = InteractiveMenu("Settings", settings_options)
        choice = menu.run()
        
        if choice == 0:  # Export
            self._export_recipes()
        elif choice == 1:  # Import
            self._import_recipes()
        elif choice == 2:  # Backup
            self._backup_data()
        elif choice == 3:  # Delete All
            self._delete_all_recipes()
        elif choice == 4:  # Change Username
            self._change_username()
        elif choice == 5:  # Advanced Stats
            self.controller.show_advanced_statistics()
    
    def _export_recipes(self):
        """Export recipes to various formats"""
        export_options = [
            "JSON Format",
            "Text Format",
            "CSV Format"
        ]
        
        menu = InteractiveMenu("Export Format", export_options)
        choice = menu.run()
        
        if choice >= 0:
            filename = input(f"\n{Color.BLUE}Export filename (without extension):{Color.RESET} ").strip()
            if filename:
                success = self.controller.export_recipes(choice, filename)
                if success:
                    ConsoleManager.print_success(f"Recipes exported successfully!")
                else:
                    ConsoleManager.print_error("Export failed!")
    
    def _import_recipes(self):
        """Import recipes from file"""
        filename = input(f"\n{Color.BLUE}Import filename:{Color.RESET} ").strip()
        if filename:
            success = self.controller.import_recipes(filename)
            if success:
                ConsoleManager.print_success("Recipes imported successfully!")
            else:
                ConsoleManager.print_error("Import failed!")
    
    def _backup_data(self):
        """Create backup of user data"""
        if self.controller.create_backup():
            ConsoleManager.print_success("Backup created successfully!")
        else:
            ConsoleManager.print_error("Backup failed!")
    
    def _delete_all_recipes(self):
        """Delete all user recipes with confirmation"""
        ConsoleManager.print_warning("This will delete ALL your recipes!")
        confirm_menu = InteractiveMenu("Are you sure?", ["Yes, Delete All", "No, Cancel"])
        
        if confirm_menu.run() == 0:
            final_confirm = input(f"\n{Color.RED}Type 'DELETE ALL' to confirm:{Color.RESET} ")
            if final_confirm == "DELETE ALL":
                if self.service.save_recipes(self.username, []):
                    ConsoleManager.print_success("All recipes deleted!")
                else:
                    ConsoleManager.print_error("Failed to delete recipes!")
    
    def _change_username(self):
        """Change current username"""
        new_username = input(f"\n{Color.BLUE}New username:{Color.RESET} ").strip().lower()
        if self._validate_username(new_username) and not self.service.user_exists(new_username):
            # Copy data to new user file
            recipes = self.service.load_recipes(self.username)
            if self.service.save_recipes(new_username, recipes):
                # Delete old user file
                old_file = self.service.get_user_file(self.username)
                os.remove(old_file)
                
                self.username = new_username
                self.controller = RecipeController(new_username)
                ConsoleManager.print_success(f"Username changed to {new_username}!")
            else:
                ConsoleManager.print_error("Failed to change username!")
        else:
            ConsoleManager.print_error("Invalid or existing username!")

if __name__ == "__main__":
    try:
        app = RecipeApp()
        app.run()
    except Exception as e:
        print(f"Critical error: {e}")
        input("Press Enter to exit...")