# Professional Recipe Management System

A feature-rich, console-based recipe management application built with Python. This system allows users to create, organize, search, and manage their personal recipe collections with an intuitive terminal interface.

## Features

### User Management
- Secure user authentication with account creation
- Personal recipe collections for each user
- Username modification capability

### Recipe Management
- **Add Recipes**: Interactive form for entering recipe details
- **Edit Recipes**: Update existing recipe information
- **Delete Recipes**: Remove recipes with confirmation
- **View Recipes**: Beautifully formatted recipe display
- **Recipe Categories**: Organize recipes by type (Appetizer, Main Course, Dessert, etc.)

### Advanced Features
- **Favorites System**: Mark and view favorite recipes
- **Recipe Rating**: Rate recipes on a 5-star scale
- **Search Functionality**: Search across all recipe fields (name, ingredients, instructions, tags)
- **Tagging System**: Organize recipes with custom tags
- **Time Tracking**: Record preparation and cooking times
- **Statistics**: View comprehensive recipe analytics

### Data Management
- **Export Recipes**: Save recipes in JSON, CSV, or plain text formats
- **Import Recipes**: Load recipes from JSON files
- **Data Backup**: Create timestamped backups of your recipe collection
- **Data Persistence**: JSON-based storage for easy sharing and backup

### Interface
- **Interactive Menus**: Arrow key navigation with fallback to number selection
- **Colorful Output**: Rich terminal interface with color-coded feedback
- **Responsive Design**: Adapts to different terminal environments
- **Error Handling**: Graceful error management with user-friendly messages

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/dykaradeniz/recipe-book-application
   cd recipe-management-system
   ```

2. Ensure you have Python 3.7+ installed:
   ```bash
   python --version
   ```

3. No additional dependencies are required - the application uses only Python standard library modules.

## Usage

Run the application with:
```bash
python main.py
```

### Getting Started
1. **Create an Account**: When first running the application, create a new user account
2. **Add Recipes**: Use the "Add New Recipe" option to begin building your collection
3. **Organize**: Categorize recipes, mark favorites, and add ratings
4. **Search**: Find recipes quickly using the search function
5. **Export**: Backup or share your recipes using the export functionality

### Navigation
- **Arrow Keys**: Navigate menus (when supported by your terminal)
- **Enter**: Select options
- **Numbers**: Direct menu selection
- **ESC/q**: Go back or exit

## Technical Architecture

### Core Components
- **Main Application**: `main.py` - Entry point and primary application flow
- **Controllers**: Handle user interactions and business logic
- **Models**: Data structures for recipes and related entities
- **Services**: Data persistence and business logic layer
- **Utilities**: Console interface components and helper functions

### Data Model
- **Recipes**: Core entities with ingredients, instructions, categories, and metadata
- **Users**: Separate JSON files for each user's recipe collection
- **Categories**: Predefined recipe categories (Appetizer, Main Course, etc.)
- **Ingredients**: Structured ingredient data with amounts and units

### Storage
- **Format**: JSON files for easy readability and portability
- **Location**: `/data/recipes_{username}.json` for each user
- **Backup**: Automatic timestamped backups

## Project Structure
```
.
├── main.py                 # Application entry point
├── controllers/
│   └── recipe_controller.py # Recipe management logic
├── models/
│   └── recipe.py           # Data models and structures
├── services/
│   └── recipe_service.py   # Data persistence layer
├── utils/
│   └── console_utils.py    # Terminal interface components
└── data/
    └── recipes_*.json      # User recipe collections
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Professional Recipe Management System was developed as a comprehensive terminal-based application for personal recipe organization and management.

---
🚀 Special thanks to [abra](https://github.com/the-abra) and [metwse](https://github.com/metwse) for their outstanding contributions and support in shaping this project.