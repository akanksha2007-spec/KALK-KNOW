"""
Kalki Know — Log In page.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QPushButton,
    QLineEdit, QMessageBox
)

from auth import verify_login, save_session

FOREST      = "#244D39"
FOREST_DEEP = "#203128"
PARCHMENT   = "#F5F2E9"
CARD        = "#FFFEFA"
INK         = "#203128"
INK_SOFT    = "#68776B"
LINE        = "#E4DFD2"
MOSS        = "#789078"


class LoginPage(QWidget):
    # emits when user successfully logs in
    logged_in = Signal(dict)
    # emits when user clicks "New here? Create account"
    switch_to_signup = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{PARCHMENT};")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(40, 36, 40, 36)
        outer.addStretch()

        card = QFrame()
        card.setFixedWidth(440)
        card.setStyleSheet(f"""
            QFrame {{
                background: {CARD};
                border: 1px solid {LINE};
                border-radius: 18px;
            }}
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(34, 34, 34, 30)
        card_layout.setSpacing(14)

        # Brand
        brand = QLabel("🌿  Kalki Know")
        brand.setStyleSheet(f"""
            color: {FOREST_DEEP};
            font-size: 19px;
            font-weight: 700;
            border: none;
            background: transparent;
        """)
        card_layout.addWidget(brand)

        # Tabs row
        tabs = QHBoxLayout()
        tabs.setSpacing(8)

        tab_login = QPushButton("Log In")
        tab_login.setCursor(Qt.PointingHandCursor)
        tab_login.setStyleSheet(f"""
            QPushButton {{
                background: {FOREST};
                border: none;
                border-radius: 9px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 700;
                color: #FFFFFF;
            }}
        """)
        tabs.addWidget(tab_login)

        tab_signup = QPushButton("Create account")
        tab_signup.setCursor(Qt.PointingHandCursor)
        tab_signup.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 9px;
                padding: 10px 18px;
                font-size: 13px;
                font-weight: 600;
                color: {INK_SOFT};
            }}
            QPushButton:hover {{
                background: #EDF1E8;
                color: {FOREST_DEEP};
            }}
        """)
        tab_signup.clicked.connect(self.switch_to_signup.emit)
        tabs.addWidget(tab_signup)
        tabs.addStretch()
        card_layout.addLayout(tabs)

        # Title
        title = QLabel("Welcome back")
        title.setStyleSheet(f"""
            color: {FOREST_DEEP};
            font-size: 25px;
            font-weight: 700;
            border: none;
            background: transparent;
            margin-top: 8px;
        """)
        card_layout.addWidget(title)

        sub = QLabel(
            "Log in to continue to your plant knowledge workspace."
        )
        sub.setStyleSheet(f"""
            color: {INK_SOFT};
            font-size: 13px;
            border: none;
            background: transparent;
        """)
        sub.setWordWrap(True)
        card_layout.addWidget(sub)

        # Fields
        def field_label(text):
            label = QLabel(text)
            label.setStyleSheet(f"""
                color: {INK};
                font-size: 12px;
                font-weight: 600;
                border: none;
                background: transparent;
            """)
            return label

        def styled_input(placeholder, password=False):
            inp = QLineEdit()
            inp.setPlaceholderText(placeholder)
            inp.setMinimumHeight(42)
            inp.setStyleSheet(f"""
                QLineEdit {{
                    background: {CARD};
                    border: 1px solid {LINE};
                    border-radius: 9px;
                    padding: 10px 12px;
                    font-size: 13px;
                    color: {INK};
                }}
                QLineEdit:focus {{
                    border: 1px solid {MOSS};
                }}
            """)
            if password:
                inp.setEchoMode(QLineEdit.Password)
            return inp

        card_layout.addSpacing(5)

        card_layout.addWidget(field_label("Username"))
        self.username_in = styled_input("e.g. ananya_rao")
        card_layout.addWidget(self.username_in)

        card_layout.addWidget(field_label("Password"))
        self.password_in = styled_input(
            "Enter your password",
            password=True
        )
        card_layout.addWidget(self.password_in)

        # Login button
        card_layout.addSpacing(8)

        login_btn = QPushButton("Log In")
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.setMinimumHeight(44)
        login_btn.setStyleSheet(f"""
            QPushButton {{
                background: {FOREST};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 18px;
                font-size: 13px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background: #193A2D;
            }}
            QPushButton:pressed {{
                background: #102B20;
            }}
        """)
        login_btn.clicked.connect(self.try_login)
        card_layout.addWidget(login_btn)

        # Bottom link
        switch_row = QHBoxLayout()
        switch_row.addStretch()

        link = QPushButton("New here?  Create an account")
        link.setCursor(Qt.PointingHandCursor)
        link.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {MOSS};
                font-size: 12px;
                font-weight: 600;
                padding: 6px;
            }}
            QPushButton:hover {{
                color: {FOREST_DEEP};
            }}
        """)
        link.clicked.connect(self.switch_to_signup.emit)
        switch_row.addWidget(link)
        switch_row.addStretch()
        card_layout.addLayout(switch_row)

        outer.addWidget(card, alignment=Qt.AlignHCenter)
        outer.addStretch()

    def try_login(self):
        username = self.username_in.text().strip()
        password = self.password_in.text()

        if not username or not password:
            QMessageBox.warning(
                self,
                "Missing fields",
                "Please enter username and password."
            )
            return

        user = verify_login(username, password)

        if not user:
            QMessageBox.warning(
                self,
                "Login failed",
                "Incorrect username or password."
            )
            return

        save_session(user)
        self.logged_in.emit(user)