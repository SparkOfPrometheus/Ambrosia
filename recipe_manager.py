# recipe_manager.py

import os

class Recipe:
    def __init__(
        self, 
        title, 
        description, 
        ingredients, 
        steps, 
        tags=None, 
        filename=None,
        is_valid=True
    ):
        self.title = title
        self.description = description
        self.ingredients = ingredients  # list of strings
        self.steps = steps  # list of strings
        self.tags = tags if tags else []  # list of strings
        self.filename = filename
        self.is_valid = is_valid

def parse_search_input(search_input):
    query = search_input.strip()
    if not query:
        return "NONE", []

    if '+' in query:
        terms = [t.strip().lower() for t in query.split('+') if t.strip()]
        return "AND", terms
    elif ',' in query:
        terms = [t.strip().lower() for t in query.split(',') if t.strip()]
        return "OR", terms
    elif ' ' in query:
        return "PHRASE", [query.lower()]
    else:
        return "PHRASE", [query.lower()]

def load_recipes(recipe_folder="recipes"):
    recipes = []
    if not os.path.exists(recipe_folder):
        os.makedirs(recipe_folder)

    for file_name in os.listdir(recipe_folder):
        if file_name.lower().endswith(".txt"):
            file_path = os.path.join(recipe_folder, file_name)
            recipe = parse_recipe_file(file_path)
            if recipe is not None:
                recipes.append(recipe)
    return recipes

def parse_recipe_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        title = ""
        description = ""
        tags = []
        ingredients = []
        steps = []
        mode = None
        is_valid = True

        for line in lines:
            line_stripped = line.strip()

            if line_stripped.startswith("Title:"):
                title = line_stripped.replace("Title:", "").strip()
                continue

            if line_stripped.startswith("Description:"):
                description = line_stripped.replace("Description:", "").strip()
                continue

            if line_stripped.startswith("Tags:"):
                tags_part = line_stripped.replace("Tags:", "").strip()
                # Split by comma
                tags = [tag.strip().lower() for tag in tags_part.split(',') if tag.strip()]
                continue

            if line_stripped.startswith("Ingredients:"):
                mode = "ingredients"
                continue

            if line_stripped.startswith("Steps:"):
                mode = "steps"
                continue

            if mode == "ingredients" and line_stripped.startswith("- "):
                ingredient_line = line_stripped.replace("- ", "").strip()
                if ingredient_line:
                    ingredients.append(ingredient_line)
                continue

            if mode == "steps" and line_stripped:
                steps.append(line_stripped)
                continue

        if not title or not description:
            is_valid = False
        if len(description) < 30:
            is_valid = False
        if not steps:
            is_valid = False

        return Recipe(
            title=title, 
            description=description, 
            ingredients=ingredients, 
            steps=steps,
            tags=tags,
            filename=file_path,
            is_valid=is_valid
        )

    except Exception as e:
        print(f"Error parsing file {file_path}: {e}")
        base_name = os.path.basename(file_path).replace(".txt", "")
        return Recipe(
            title=base_name, 
            description="Error reading file.",
            ingredients=[],
            steps=[],
            tags=[],
            filename=file_path,
            is_valid=False
        )

def search_recipes(recipes, search_query, selected_tags=None):
    mode, terms = parse_search_input(search_query)
    if selected_tags is None:
        selected_tags = []

    def has_all_tags(recipe, tags_list):
        return all(t.lower() in recipe.tags for t in tags_list if t.strip())

    filtered_by_tags = [r for r in recipes if has_all_tags(r, selected_tags)]

    if mode == "NONE":
        return filtered_by_tags

    results = []
    for recipe in filtered_by_tags:
        combined_text = (
            recipe.title.lower() + " " 
            + recipe.description.lower() + " " 
            + " ".join(recipe.ingredients).lower()
        )

        if mode == "AND":
            if all(term in combined_text for term in terms):
                results.append(recipe)
        elif mode == "OR":
            if any(term in combined_text for term in terms):
                results.append(recipe)
        elif mode == "PHRASE":
            phrase = terms[0]
            if phrase in combined_text:
                results.append(recipe)
    return results

def add_recipe(
    title, 
    description, 
    ingredients, 
    steps, 
    tags=None, 
    recipe_folder="recipes"
):
    if len(description) < 30:
        raise ValueError("Description must be at least 30 characters.")

    file_name = title.lower().replace(" ", "_") + ".txt"
    file_path = os.path.join(recipe_folder, file_name)

    if not os.path.exists(recipe_folder):
        os.makedirs(recipe_folder)

    if tags is None:
        tags = []

    lines = []
    lines.append(f"Title: {title}")
    lines.append(f"Description: {description}")
    if tags:
        lines.append("Tags: " + ", ".join(tags))
    else:
        lines.append("Tags: ")
    lines.append("Ingredients:")
    for ing in ingredients:
        ing_formatted = ing.strip().replace(" ", "_")
        lines.append(f"- {ing_formatted}")
    lines.append("Steps:")
    for i, step in enumerate(steps, 1):
        lines.append(f"{i}. {step}")

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")
        print(f"Recipe saved at: {file_path}")  # Debug
        return file_path
    except Exception as e:
        print(f"Failed to write recipe file: {e}")
        return None

def update_recipe(recipe_obj, new_title, new_description, new_ingredients, new_steps, new_tags):
    if not recipe_obj.filename:
        return False

    if len(new_description) < 30:
        raise ValueError("Description must be at least 30 characters.")

    lines = []
    lines.append(f"Title: {new_title}")
    lines.append(f"Description: {new_description}")
    if new_tags:
        lines.append("Tags: " + ", ".join(new_tags))
    else:
        lines.append("Tags: ")
    lines.append("Ingredients:")
    for ing in new_ingredients:
        ing_formatted = ing.strip().replace(" ", "_")
        lines.append(f"- {ing_formatted}")
    lines.append("Steps:")
    for i, step in enumerate(new_steps, 1):
        lines.append(f"{i}. {step}")

    try:
        with open(recipe_obj.filename, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")
        return True
    except Exception as e:
        print(f"Failed to update recipe file: {e}")
        return False

def delete_recipe(recipe_obj):
    if recipe_obj.filename and os.path.exists(recipe_obj.filename):
        try:
            os.remove(recipe_obj.filename)
            return True
        except Exception as e:
            print(f"Failed to delete {recipe_obj.filename}: {e}")
            return False
    return False

def validate_recipes(recipes):
    invalids = [r for r in recipes if not r.is_valid]
    return invalids
