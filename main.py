"""
Kalki Know — entry point.
Run:  python main.py
"""

import sys
import os
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication

from auth import load_session
from auth_window import AuthWindow
from shell import Shell

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(BASE_DIR, "logo.ico")

def launch_shell(user):
    global shell_window
    shell_window = Shell(user)
    if os.path.exists(ICON_PATH):
        shell_window.setWindowIcon(QIcon(ICON_PATH))
    shell_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    
    # ---------------- GLOBAL UI STYLING (PREMIUM BOTANICAL) ----------------
    app.setStyleSheet("""
        QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {
            background: #FFFEFA;
            color: #1D2C24;
            border: 1px solid #D8DCCF;
            border-radius: 9px;
            padding: 9px 11px;
            selection-background-color: #2B5945;
            selection-color: #FFFFFF;
        }
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {
            border: 1px solid #718A70;
        }
        QPushButton {
            border-radius: 9px;
        }
        QToolTip {
            background: #17382B;
            color: #FFFFFF;
            border: 1px solid #718A70;
            border-radius: 6px;
            padding: 6px 8px;
        }
        QCheckBox {
            color: #1D2C24;
            spacing: 8px;
        }
        QComboBox QAbstractItemView {
            background: #FFFEFA;
            color: #1D2C24;
            selection-background-color: #E2EDE2;
            selection-color: #17382B;
            border: 1px solid #E2DDCF;
        }
    """)
    # -----------------------------------------------------------------------

    if os.path.exists(ICON_PATH):
        app.setWindowIcon(QIcon(ICON_PATH))

    existing_session = load_session()
    if existing_session:
        launch_shell(existing_session)
    else:
        auth = AuthWindow(on_success=launch_shell)
        if os.path.exists(ICON_PATH):
            auth.setWindowIcon(QIcon(ICON_PATH))
        auth.show()

    sys.exit(app.exec())