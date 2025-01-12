# Ambrosia
A minimalist recipe manager


![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)

**AMBROSIA!** is a feature-rich recipe management application built with Python and PySide6 (Qt for Python). It allows users to add, edit, search, and organize their favorite recipes with ease. The application supports advanced search capabilities, tag filtering, customizable appearance settings, and ensures data integrity through validation checks.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Code Structure](#code-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Add Recipes:** Easily add new recipes with detailed descriptions, ingredients, steps, and tags.
- **Edit & Delete:** Modify existing recipes or remove them entirely using a convenient context menu.
- **Advanced Search:** Perform complex searches using AND (`+`), OR (`,`), and phrase (`" "`) operators.
- **Tag Filtering:** Filter recipes based on predefined or custom tags to quickly find what you're looking for.
- **Appearance Settings:** Customize the application's appearance with options for font family, size, boldness, and dark/light mode.
- **Data Validation:** Ensure all recipes meet required standards with built-in validation checks.
- **Persistent Settings:** User preferences are saved and loaded automatically, providing a consistent experience across sessions.

## Installation

### Prerequisites

- **Python 3.7+**: Ensure you have Python installed. You can download it from [python.org](https://www.python.org/downloads/).

### Clone the Repository


git clone https://github.com/sparkofprometheus/AMBROSIA.git
cd AMBROSIA

###Create a Virtual Environment (Optional but Recommended)


python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

###Install Dependencies


pip install -r requirements.txt
If requirements.txt is not provided, install PySide6 directly:


pip install PySide6

###Run the Application


python main.py

##Usage

###Adding a Recipe
Open the Add Recipe Dialog

Click on File > Add Recipe or press Ctrl+N.
Fill in the Recipe Details

Title: Enter the recipe name.
Description: Provide a detailed description (minimum 30 characters).
Tags: Select existing tags or add new ones in the "Additional Tags" field.
Ingredients: List ingredients, one per line.
Steps: Outline the preparation steps, one per line.
Save the Recipe

Click Save to add the recipe. It will appear in the recipe list and be saved in the recipes/ folder.

##Editing or Deleting a Recipe
Access the Context Menu

Right-click on a recipe in the list.
Choose an Action

Edit: Modify the recipe details.
Delete: Remove the recipe permanently.

##Searching for Recipes
Use the Search Bar

Enter keywords, exact phrases, or use + for AND logic and , for OR logic.
Examples:
"pancakes": Finds recipes containing "pancakes".
"fluffy breakfast": Searches for the exact phrase "fluffy breakfast".
"milk+egg": Finds recipes containing both "milk" and "egg".
"pancake, flour": Finds recipes containing either "pancake" or "flour".
Filter by Tags

Select or deselect tag checkboxes to narrow down recipes based on categories like Breakfast, Dessert, etc.
Appearance Settings
Access Appearance Options

Navigate to Appearance in the menu bar.


###Customize Settings

Scale: Choose between Small, Medium, or Large text sizes.
Font: Select from Serif, Sans-Serif, or Script fonts.
Bold: Toggle bold text on or off.
Dark Mode: Switch between light and dark themes.
Settings Persistence

Your appearance preferences are saved automatically and loaded on subsequent application launches.
Checking for Malformed Recipes
Run Validation

Go to File > Check Recipes.
Review Results

The application will highlight any malformed recipes in red and provide a summary of issues.

###Code Structure

AMBROSIA/
├── main.py
├── gui.py
├── recipe_manager.py
├── settings_manager.py
├── requirements.txt        # If available
├── settings.json           # Created automatically on first run
└── recipes/
    └── (your .txt recipe files)
##Description of Files
main.py

Entry point of the application.
Initializes the application, ensures the recipes/ folder exists, and launches the main window.
gui.py

Contains the graphical user interface components.
Defines classes for the main window (AMBROSIA), add/edit recipe dialogs (AddRecipeDialog, EditRecipeDialog).
Handles user interactions, appearance settings, and recipe display.
recipe_manager.py

Manages recipe-related operations.
Functions to load, parse, search, add, edit, delete, and validate recipes.
Defines the Recipe class representing individual recipes.
settings_manager.py

Handles loading and saving user settings to settings.json.
Manages default settings and ensures user preferences are persisted.
recipes/

Directory where all recipe .txt files are stored.
Each recipe follows a structured format with sections like Title, Description, Tags, Ingredients, and Steps.
Contributing
Contributions are welcome! Please follow these steps:

Fork the Repository

Create a New Branch


git checkout -b feature/YourFeature
Commit Your Changes


git commit -m "Add your message here"
Push to the Branch


git push origin feature/YourFeature
Open a Pull Request

Describe your changes and submit the pull request for review.

License
This project is licensed under the GNU General Public License v3.0 (GPL-3.0).


GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

[Full GPL-3.0 license text here]
Please refer to the LICENSE file in the repository for the complete license text.
