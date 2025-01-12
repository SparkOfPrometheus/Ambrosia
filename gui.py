import os
import sys

from PySide6.QtCore import Qt, Slot, QPoint
from PySide6.QtGui import QAction, QKeySequence, QFont
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QListWidget, QListWidgetItem, QMessageBox, QApplication,
    QMenuBar, QMenu, QPushButton, QDialog, QFormLayout,
    QLineEdit, QTextEdit, QCheckBox, QLabel, QDialogButtonBox,
    QSpacerItem, QSizePolicy, QGroupBox
)

import recipe_manager
import settings_manager


class AddRecipeDialog(QDialog):
    """
    Dialog for adding a new recipe, with checkboxes for known tags plus a field to add custom tags.
    """
    def __init__(self, known_tags, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Recipe")
        self.resize(500, 450)

        self.title_edit = QLineEdit()
        self.desc_edit = QTextEdit()
        self.ing_edit = QTextEdit()
        self.steps_edit = QTextEdit()

        # Tag checkboxes
        self.tag_checkboxes = []
        self.tag_box_layout = QHBoxLayout()
        for t in known_tags:
            cb = QCheckBox(t.capitalize())
            self.tag_checkboxes.append(cb)
            self.tag_box_layout.addWidget(cb)

        # Field to add additional tags
        self.new_tag_edit = QLineEdit()
        self.new_tag_edit.setPlaceholderText("Add new tags (comma-separated)")

        layout = QFormLayout()
        layout.addRow("Title:", self.title_edit)
        layout.addRow("Description (30+ chars):", self.desc_edit)
        # Group box for known tags
        tag_group = QGroupBox("Select Tags:")
        g_layout = QVBoxLayout()
        g_layout.addLayout(self.tag_box_layout)
        tag_group.setLayout(g_layout)
        layout.addRow(tag_group)
        layout.addRow("Additional Tags:", self.new_tag_edit)
        layout.addRow("Ingredients (one per line):", self.ing_edit)
        layout.addRow("Steps (one per line):", self.steps_edit)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.save_recipe)
        self.button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)

        self.saved_recipe_path = None

    @Slot()
    def save_recipe(self):
        title = self.title_edit.text().strip()
        description = self.desc_edit.toPlainText().strip()
        ingredients_raw = self.ing_edit.toPlainText().splitlines()
        steps_raw = self.steps_edit.toPlainText().splitlines()

        # gather selected tags
        selected_tags = []
        for cb in self.tag_checkboxes:
            if cb.isChecked():
                selected_tags.append(cb.text().lower())

        # parse additional tags
        extra_tags = self.new_tag_edit.text().split(',')
        for t in extra_tags:
            tt = t.strip().lower()
            if tt:
                selected_tags.append(tt)

        ingredients = [line.strip() for line in ingredients_raw if line.strip()]
        steps = [line.strip() for line in steps_raw if line.strip()]

        if not title:
            QMessageBox.warning(self, "Validation Error", "Title cannot be empty.")
            return
        
        if len(description) < 30:
            QMessageBox.warning(self, "Validation Error", 
                                "Description must be at least 30 characters.")
            return
        
        if len(description) > 300:
            reply = QMessageBox.question(
                self,
                "Long Description",
                "Description is over 300 characters. Proceed anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        try:
            recipe_path = recipe_manager.add_recipe(
                title=title,
                description=description,
                ingredients=ingredients,
                steps=steps,
                tags=selected_tags
            )
            if recipe_path:
                QMessageBox.information(self, "Success", "Recipe added successfully!")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to save recipe file.")
        except ValueError as ve:
            QMessageBox.warning(self, "Validation Error", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unexpected error:\n{e}")


class EditRecipeDialog(QDialog):
    """
    Dialog for editing an existing recipe. 
    Also shows checkboxes for known tags, plus a field to add new tags.
    """
    def __init__(self, recipe_obj, known_tags, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Recipe")
        self.resize(500, 450)
        self.recipe_obj = recipe_obj

        self.title_edit = QLineEdit(recipe_obj.title)
        self.desc_edit = QTextEdit(recipe_obj.description)
        self.ing_edit = QTextEdit("\n".join(recipe_obj.ingredients))
        self.steps_edit = QTextEdit("\n".join(recipe_obj.steps))

        # known tags checkboxes
        self.tag_checkboxes = []
        self.tag_box_layout = QHBoxLayout()
        current_tags_lower = [t.lower() for t in recipe_obj.tags]
        for t in known_tags:
            cb = QCheckBox(t.capitalize())
            if t.lower() in current_tags_lower:
                cb.setChecked(True)
            self.tag_checkboxes.append(cb)
            self.tag_box_layout.addWidget(cb)

        # additional tags field
        self.new_tag_edit = QLineEdit()
        self.new_tag_edit.setPlaceholderText("Add new tags (comma-separated)")

        layout = QFormLayout()
        layout.addRow("Title:", self.title_edit)
        layout.addRow("Description (30+ chars):", self.desc_edit)

        tag_group = QGroupBox("Select Tags:")
        g_layout = QVBoxLayout()
        g_layout.addLayout(self.tag_box_layout)
        tag_group.setLayout(g_layout)
        layout.addRow(tag_group)
        layout.addRow("Additional Tags:", self.new_tag_edit)
        layout.addRow("Ingredients (one per line):", self.ing_edit)
        layout.addRow("Steps (one per line):", self.steps_edit)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.save_changes)
        self.button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)

    @Slot()
    def save_changes(self):
        new_title = self.title_edit.text().strip()
        new_description = self.desc_edit.toPlainText().strip()
        new_ing_raw = self.ing_edit.toPlainText().splitlines()
        new_steps_raw = self.steps_edit.toPlainText().splitlines()

        # gather selected tags from checkboxes
        selected_tags = []
        for cb in self.tag_checkboxes:
            if cb.isChecked():
                selected_tags.append(cb.text().lower())

        # parse additional tags
        extra_tags = self.new_tag_edit.text().split(',')
        for t in extra_tags:
            tt = t.strip().lower()
            if tt:
                selected_tags.append(tt)

        new_ingredients = [i.strip() for i in new_ing_raw if i.strip()]
        new_steps = [s.strip() for s in new_steps_raw if s.strip()]

        if not new_title:
            QMessageBox.warning(self, "Validation Error", "Title cannot be empty.")
            return
        if len(new_description) < 30:
            QMessageBox.warning(self, "Validation Error", 
                                "Description must be at least 30 characters.")
            return

        try:
            success = recipe_manager.update_recipe(
                recipe_obj=self.recipe_obj,
                new_title=new_title,
                new_description=new_description,
                new_ingredients=new_ingredients,
                new_steps=new_steps,
                new_tags=selected_tags
            )
            if success:
                QMessageBox.information(self, "Success", "Recipe updated successfully!")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to update recipe file.")
        except ValueError as ve:
            QMessageBox.warning(self, "Validation Error", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unexpected error:\n{e}")


class AMBROSIA(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AMBROSIA!")
        self.resize(1000, 600)

        # Load settings
        self.settings = settings_manager.load_settings()

        # Load recipes
        self.recipes = recipe_manager.load_recipes()

        # The user can define default tags in settings. We'll also gather all tags from existing recipes.
        all_tags = set(self.settings.get("default_tags", []))
        for r in self.recipes:
            for t in r.tags:
                all_tags.add(t.lower())
        self.all_known_tags = sorted(all_tags)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Tag filter row
        tag_layout = QHBoxLayout()
        tag_layout.addWidget(QLabel("Filter by tags:"))
        self.tag_checkboxes = []
        for t in self.all_known_tags:
            cb = QCheckBox(t.capitalize())
            cb.stateChanged.connect(self.on_tag_filter_changed)
            self.tag_checkboxes.append(cb)
            tag_layout.addWidget(cb)
        main_layout.addLayout(tag_layout)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search recipes... (space=phrase, + AND, , OR)")
        self.search_bar.returnPressed.connect(self.perform_search)
        main_layout.addWidget(self.search_bar)

        # Recipe list
        self.recipe_list = QListWidget()
        self.recipe_list.itemDoubleClicked.connect(self.show_recipe_detail)
        self.recipe_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.recipe_list.customContextMenuRequested.connect(self.show_context_menu)
        main_layout.addWidget(self.recipe_list)

        self.display_recipes(self.recipes)

        # Menu Bar
        self.create_menu_bar()

        # Apply appearance (font, scale, bold, dark_mode) from settings
        self.apply_appearance()

        # Shortcuts
        self.register_shortcuts()

    def closeEvent(self, event):
        """
        Called when the window closes.
        We save the settings to disk here.
        """
        settings_manager.save_settings(self.settings)
        super().closeEvent(event)

    def create_menu_bar(self):
        menu_bar = QMenuBar()

        # File Menu
        file_menu = QMenu("File", self)
        add_recipe_action = QAction("Add Recipe", self)
        add_recipe_action.setShortcut(QKeySequence("Ctrl+N"))
        add_recipe_action.triggered.connect(self.open_add_dialog)
        file_menu.addAction(add_recipe_action)

        check_recipes_action = QAction("Check Recipes", self)
        check_recipes_action.triggered.connect(self.check_recipes)
        file_menu.addAction(check_recipes_action)

        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        menu_bar.addMenu(file_menu)

        # Appearance Menu
        appearance_menu = QMenu("Appearance", self)

        # Scale sub-menu
        scale_menu = QMenu("Scale", self)
        self.scale_small_action = QAction("Small", self, checkable=True)
        self.scale_medium_action = QAction("Medium", self, checkable=True)
        self.scale_large_action = QAction("Large", self, checkable=True)

        self.scale_small_action.triggered.connect(lambda: self.set_scale(9))
        self.scale_medium_action.triggered.connect(lambda: self.set_scale(10))
        self.scale_large_action.triggered.connect(lambda: self.set_scale(12))

        scale_menu.addAction(self.scale_small_action)
        scale_menu.addAction(self.scale_medium_action)
        scale_menu.addAction(self.scale_large_action)

        # Font sub-menu
        font_menu = QMenu("Font", self)
        self.font_serif_action = QAction("Serif", self, checkable=True)
        self.font_sans_action = QAction("Sans-Serif", self, checkable=True)
        self.font_script_action = QAction("Script", self, checkable=True)

        self.font_serif_action.triggered.connect(lambda: self.set_font_family("Times New Roman"))
        self.font_sans_action.triggered.connect(lambda: self.set_font_family("Arial"))
        self.font_script_action.triggered.connect(lambda: self.set_font_family("Comic Sans MS"))

        font_menu.addAction(self.font_serif_action)
        font_menu.addAction(self.font_sans_action)
        font_menu.addAction(self.font_script_action)

        # Bold toggle
        self.bold_action = QAction("Bold", self, checkable=True)
        self.bold_action.triggered.connect(self.toggle_bold)

        # Dark mode
        self.dark_mode_action = QAction("Dark Mode", self, checkable=True)
        self.dark_mode_action.triggered.connect(self.toggle_dark_mode)

        appearance_menu.addMenu(scale_menu)
        appearance_menu.addMenu(font_menu)
        appearance_menu.addAction(self.bold_action)
        appearance_menu.addAction(self.dark_mode_action)

        menu_bar.addMenu(appearance_menu)
        self.setMenuBar(menu_bar)

        # Sync the check states with current settings
        self.sync_appearance_menu_checks()

    def apply_appearance(self):
        """Apply appearance settings recursively to all widgets"""
        # Create base font
        font = QFont(self.settings["font_family"], self.settings["font_size"])
        font.setBold(self.settings["font_bold"])
        
        # Apply font recursively to all widgets
        self.apply_font_recursive(self, font)
        
        # Apply dark/light mode
        if self.settings["is_dark_mode"]:
            self.setStyleSheet("""
                QMainWindow, QDialog {
                    background-color: #2E2E2E;
                    color: #EAEAEA;
                }
                QWidget {
                    background-color: #2E2E2E;
                    color: #EAEAEA;
                }
                QLineEdit, QTextEdit, QListWidget, QMenuBar, QMenu, QGroupBox {
                    background-color: #3C3C3C;
                    color: #EAEAEA;
                    border: 1px solid #4A4A4A;
                }
                QCheckBox {
                    background-color: transparent;
                    color: #EAEAEA;
                }
                QMessageBox {
                    background-color: #2E2E2E;
                    color: #EAEAEA;
                }
                QLabel {
                    background-color: transparent;
                    color: #EAEAEA;
                }
                QPushButton {
                    background-color: #3C3C3C;
                    color: #EAEAEA;
                    border: 1px solid #4A4A4A;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #4A4A4A;
                }
                QMenuBar::item:selected, QMenu::item:selected {
                    background-color: #4A4A4A;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow, QDialog {
                    background-color: #F5F5F5;
                    color: #000000;
                }
                QWidget {
                    background-color: #F5F5F5;
                    color: #000000;
                }
                QLineEdit, QTextEdit, QListWidget, QMenuBar, QMenu, QGroupBox {
                    background-color: #FFFFFF;
                    color: #000000;
                    border: 1px solid #CCCCCC;
                }
                QCheckBox {
                    background-color: transparent;
                    color: #000000;
                }
                QMessageBox {
                    background-color: #F5F5F5;
                    color: #000000;
                }
                QLabel {
                    background-color: transparent;
                    color: #000000;
                }
                QPushButton {
                    background-color: #FFFFFF;
                    color: #000000;
                    border: 1px solid #CCCCCC;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #EFEFEF;
                }
                QMenuBar::item:selected, QMenu::item:selected {
                    background-color: #E0E0E0;
                }
            """)

    def apply_font_recursive(self, widget, font):
        """Recursively apply font to widget and all its children"""
        widget.setFont(font)
        
        # Special handling for QMenu items
        if isinstance(widget, QMenuBar):
            for action in widget.actions():
                if action.menu():
                    action.menu().setFont(font)
        
        # Apply to all child widgets
        for child in widget.findChildren(QWidget):
            self.apply_font_recursive(child, font)

    def set_scale(self, pt_size):
        """Update font size and reapply appearance"""
        if pt_size != self.settings["font_size"]:
            self.settings["font_size"] = pt_size
            self.apply_appearance()
            self.sync_appearance_menu_checks()

    def set_font_family(self, family):
        """Update font family and reapply appearance"""
        if family != self.settings["font_family"]:
            self.settings["font_family"] = family
            self.apply_appearance()
            self.sync_appearance_menu_checks()

    def toggle_bold(self):
        """Toggle bold setting and reapply appearance"""
        self.settings["font_bold"] = not self.settings["font_bold"]
        self.apply_appearance()
        self.sync_appearance_menu_checks()

    def toggle_dark_mode(self):
        """Toggle dark mode and reapply appearance"""
        self.settings["is_dark_mode"] = not self.settings["is_dark_mode"]
        self.apply_appearance()
        self.sync_appearance_menu_checks()

    def sync_appearance_menu_checks(self):
        """Sync menu checkmarks with current settings"""
        # Scale
        fsize = self.settings["font_size"]
        self.scale_small_action.setChecked(fsize == 9)
        self.scale_medium_action.setChecked(fsize == 10)
        self.scale_large_action.setChecked(fsize == 12)

        # Font
        ff = self.settings["font_family"]
        self.font_serif_action.setChecked(ff == "Times New Roman")
        self.font_sans_action.setChecked(ff == "Arial")
        self.font_script_action.setChecked(ff == "Comic Sans MS")

        # Bold
        self.bold_action.setChecked(self.settings["font_bold"])

        # Dark mode
        self.dark_mode_action.setChecked(self.settings["is_dark_mode"])

    def display_recipes(self, recipes):
        self.recipe_list.clear()
        for recipe in recipes:
            item = QListWidgetItem(recipe.title)
            item.setData(Qt.UserRole, recipe)
            if not recipe.is_valid:
                item.setForeground(Qt.red)
            self.recipe_list.addItem(item)

    def perform_search(self):
        query = self.search_bar.text()
        selected_tags = self.get_selected_tags()
        results = recipe_manager.search_recipes(self.recipes, query, selected_tags)
        self.display_recipes(results)

    def get_selected_tags(self):
        chosen = []
        for cb in self.tag_checkboxes:
            if cb.isChecked():
                chosen.append(cb.text().lower())
        return chosen

    @Slot(int)
    def on_tag_filter_changed(self, state):
        self.perform_search()

    def show_recipe_detail(self, item):
        recipe = item.data(Qt.UserRole)
        detail_msg = (
            f"<b>{recipe.title}</b><br>"
            f"<i>Description:</i> {recipe.description}<br><br>"
            f"<i>Tags:</i> {', '.join(recipe.tags)}<br><br>"
            f"<i>Ingredients:</i><br>"
        )
        for ing in recipe.ingredients:
            detail_msg += f" - {ing}<br>"
        detail_msg += "<br><i>Steps:</i><br>"
        for step in recipe.steps:
            detail_msg += f"{step}<br>"

        QMessageBox.information(self, recipe.title, detail_msg)

    def show_context_menu(self, position: QPoint):
        item = self.recipe_list.itemAt(position)
        if not item:
            return
        recipe = item.data(Qt.UserRole)

        menu = QMenu(self)
        edit_action = QAction("Edit", self)
        delete_action = QAction("Delete", self)

        edit_action.triggered.connect(lambda: self.edit_recipe(recipe))
        delete_action.triggered.connect(lambda: self.delete_recipe(recipe))

        menu.addAction(edit_action)
        menu.addAction(delete_action)
        menu.exec(self.recipe_list.mapToGlobal(position))

    def edit_recipe(self, recipe_obj):
        dialog = EditRecipeDialog(recipe_obj, self.all_known_tags, self)
        if dialog.exec() == QDialog.Accepted:
            # Reload recipes from disk so we see the updated file
            self.recipes = recipe_manager.load_recipes()
            # Also re-gather possible tags (in case user added new ones)
            new_tags = set(self.settings["default_tags"])
            for r in self.recipes:
                for t in r.tags:
                    new_tags.add(t.lower())
            self.all_known_tags = sorted(new_tags)
            self.perform_search()

    def delete_recipe(self, recipe_obj):
        reply = QMessageBox.question(
            self,
            "Delete Recipe",
            f"Are you sure you want to delete '{recipe_obj.title}'?\nThis action cannot be undone!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            success = recipe_manager.delete_recipe(recipe_obj)
            if success:
                QMessageBox.information(self, "Deleted", f"'{recipe_obj.title}' was deleted.")
                self.recipes = recipe_manager.load_recipes()
                self.perform_search()

    def open_add_dialog(self):
        dialog = AddRecipeDialog(self.all_known_tags, self)
        if dialog.exec() == QDialog.Accepted:
            self.recipes = recipe_manager.load_recipes()
            # Also re-gather possible tags
            new_tags = set(self.settings["default_tags"])
            for r in self.recipes:
                for t in r.tags:
                    new_tags.add(t.lower())
            self.all_known_tags = sorted(new_tags)
            self.perform_search()

    def check_recipes(self):
        invalids = recipe_manager.validate_recipes(self.recipes)
        if not invalids:
            QMessageBox.information(self, "Check Recipes", "All recipes are valid!")
        else:
            self.display_recipes(self.recipes)
            msg = "Some recipes appear malformed:\n"
            for r in invalids:
                base_file = os.path.basename(r.filename) if r.filename else r.title
                msg += f" - {base_file}\n"
            QMessageBox.warning(self, "Malformed Recipes", msg)

    def register_shortcuts(self):
        search_action = QAction(self)
        search_action.setShortcut(QKeySequence("Ctrl+F"))
        search_action.triggered.connect(lambda: self.search_bar.setFocus())
        self.addAction(search_action)