# models/recipe.py
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum
import uuid

class RecipeCategory(Enum):
    APPETIZER = "Appetizer"
    MAIN_COURSE = "Main Course"
    DESSERT = "Dessert"
    BEVERAGE = "Beverage"
    SOUP = "Soup"
    SALAD = "Salad"
    SNACK = "Snack"
    BREAKFAST = "Breakfast"

@dataclass
class Ingredient:
    name: str
    amount: str
    unit: str = ""
    
    def __str__(self) -> str:
        return f"{self.amount} {self.unit} {self.name}".strip()

@dataclass
class NutritionalInfo:
    calories: Optional[int] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    fiber: Optional[float] = None

@dataclass
class Recipe:
    name: str
    ingredients: List[Ingredient]
    instructions: List[str]
    category: RecipeCategory
    is_favorite: bool = False
    prep_time: Optional[int] = None  # in minutes
    cook_time: Optional[int] = None  # in minutes
    servings: Optional[int] = None
    difficulty: str = "Medium"
    tags: List[str] = None
    nutritional_info: Optional[NutritionalInfo] = None
    rating: Optional[float] = None
    notes: str = ""
    created_at: str = None
    updated_at: str = None
    recipe_id: str = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at
        if self.recipe_id is None:
            self.recipe_id = str(uuid.uuid4())
    
    @property
    def total_time(self) -> Optional[int]:
        if self.prep_time and self.cook_time:
            return self.prep_time + self.cook_time
        return self.prep_time or self.cook_time
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['category'] = self.category.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Recipe':
        # Handle category conversion
        if isinstance(data.get('category'), str):
            try:
                data['category'] = RecipeCategory(data['category'])
            except ValueError:
                data['category'] = RecipeCategory.MAIN_COURSE
        
        # Handle ingredients conversion
        if 'ingredients' in data:
            ingredients = []
            for ing_data in data['ingredients']:
                if isinstance(ing_data, dict):
                    ingredients.append(Ingredient(**ing_data))
                else:
                    # Handle legacy format
                    ingredients.append(Ingredient(
                        name=ing_data.get('name', ''),
                        amount=ing_data.get('amount', ''),
                        unit=ing_data.get('unit', '')
                    ))
            data['ingredients'] = ingredients
        
        # Handle nutritional info
        if 'nutritional_info' in data and data['nutritional_info']:
            data['nutritional_info'] = NutritionalInfo(**data['nutritional_info'])
        
        return cls(**data)