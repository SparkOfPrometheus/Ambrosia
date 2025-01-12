# main.py

import sys
import os
from PySide6.QtWidgets import QApplication
from gui import AMBROSIA

def main():
    # Make sure 'recipes' folder exists
    if not os.path.exists("recipes"):
        os.makedirs("recipes")

    app = QApplication(sys.argv)
    window = AMBROSIA()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
