"""
Kalki Know — Create Account page.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QPushButton,
    QLineEdit, QMessageBox, QComboBox
)

from auth import create_user, verify_login, save_session, ROLES

FOREST      = "#1B4332"
FOREST_DEEP = "#122C21"
PARCHMENT   = "#FAF7F0"
CARD        = "#FFFFFF"
INK         = "#22281F"
INK_SOFT    = "#5B6358"
LINE        = "#E4E0D4"
MOSS        = "#52796F"


class SignupPage(QWidget):
    account_created = Signal(dict)   # auto-login after signup
    switch_to_login = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{PARCHMENT};")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(40, 40, 40, 40)
        outer.addStretch()

        card = QFrame()
        card.setFixedWidth(440)
        card.setStyleSheet(f"QFrame {{ background:{CARD}; border:1px solid {LINE}; border-radius:12px; }}")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 32, 32, 28)
        card_layout.setSpacing(12)

        brand = QLabel("🌿  Kalki Know")
        brand.setStyleSheet(f"color:{FOREST_DEEP}; font-size:16px; font-weight:700; border:none;")
        card_layout.addWidget(brand)

        # Tabs
        tabs = QHBoxLayout()
        tab_login = QPushButton("Log In")
        tab_login.setStyleSheet(f"""
            QPushButton {{ background:transparent; border:none; border-radius:8px;
                           padding:9px 18px; font-size:13px; font-weight:600;
                           color:{INK_SOFT}; }}
            QPushButton:hover {{ color:{FOREST_DEEP}; }}
        """)
        tab_login.clicked.connect(self.switch_to_login.emit)
        tabs.addWidget(tab_login)

        tab_signup = QPushButton("Create account")
        tab_signup.setStyleSheet(f"""
            QPushButton {{ background:#F1EEE3; border:none; border-radius:8px;
                           padding:9px 18px; font-size:13px; font-weight:700;
                           color:{FOREST_DEEP}; }}
        """)
        tabs.addWidget(tab_signup)
        tabs.addStretch()
        card_layout.addLayout(tabs)

        title = QLabel("Create your account")
        title.setStyleSheet(f"color:{FOREST_DEEP}; font-size:22px; font-weight:700; border:none; margin-top:6px;")
        card_layout.addWidget(title)

        sub = QLabel("Tell us a bit about yourself so we can tailor what you see.")
        sub.setStyleSheet(f"color:{INK_SOFT}; font-size:12.5px; border:none;")
        sub.setWordWrap(True)
        card_layout.addWidget(sub)

        def field_label(text):
            l = QLabel(text)
            l.setStyleSheet(f"color:{INK}; font-size:12px; font-weight:600; border:none;")
            return l

        def styled_input(placeholder, password=False):
            inp = QLineEdit()
            inp.setPlaceholderText(placeholder)
            inp.setStyleSheet(f"""
                QLineEdit {{ background:{CARD}; border:1px solid {LINE};
                             border-radius:8px; padding:10px 12px;
                             font-size:13px; color:{INK}; }}
                QLineEdit:focus {{ border-color:{MOSS}; }}
            """)
            if password:
                inp.setEchoMode(QLineEdit.Password)
            return inp

        card_layout.addSpacing(6)
        card_layout.addWidget(field_label("Username"))
        self.username_in = styled_input("e.g. ananya_rao")
        card_layout.addWidget(self.username_in)

        card_layout.addWidget(field_label("Email address"))
        self.email_in = styled_input("you@example.com")
        card_layout.addWidget(self.email_in)

        card_layout.addWidget(field_label("Password"))
        self.password_in = styled_input("At least 8 characters", password=True)
        card_layout.addWidget(self.password_in)

        card_layout.addWidget(field_label("I am a…"))
        self.role_in = QComboBox()
        self.role_in.addItem("Select your role")
        for r in ROLES:
            self.role_in.addItem(r)
        self.role_in.setStyleSheet(f"""
            QComboBox {{ background:{CARD}; border:1px solid {LINE};
                         border-radius:8px; padding:10px 12px;
                         font-size:13px; color:{INK}; }}
            QComboBox:focus {{ border-color:{MOSS}; }}
        """)
        card_layout.addWidget(self.role_in)

        card_layout.addSpacing(8)
        create_btn = QPushButton("Create account")
        create_btn.setStyleSheet(f"""
            QPushButton {{ background:{FOREST}; color:white; border:none;
                           border-radius:8px; padding:12px 18px;
                           font-size:13px; font-weight:700; }}
            QPushButton:hover {{ background:#2E5A46; }}
        """)
        create_btn.clicked.connect(self.try_signup)
        card_layout.addWidget(create_btn)

        footer = QLabel(
            "By continuing you agree this app works offline — "
            "your data stays on this device unless you choose to sync."
        )
        footer.setStyleSheet(f"color:{INK_SOFT}; font-size:10.5px; border:none;")
        footer.setWordWrap(True)
        card_layout.addWidget(footer)

        switch_row = QHBoxLayout()
        switch_row.addStretch()
        link = QPushButton("Already have an account?  Log in")
        link.setStyleSheet(f"""
            QPushButton {{ background:transparent; border:none; color:{MOSS};
                           font-size:12px; font-weight:600; padding:4px; }}
            QPushButton:hover {{ color:{FOREST_DEEP}; }}
        """)
        link.clicked.connect(self.switch_to_login.emit)
        switch_row.addWidget(link)
        switch_row.addStretch()
        card_layout.addLayout(switch_row)

        outer.addWidget(card, alignment=Qt.AlignHCenter)
        outer.addStretch()

    def try_signup(self):
        username = self.username_in.text().strip()
        email = self.email_in.text().strip()
        password = self.password_in.text()
        role = self.role_in.currentText()

        if role == "Select your role":
            QMessageBox.warning(self, "Missing role", "Please select your role.")
            return

        ok, msg = create_user(username, email, password, role)
        if not ok:
            QMessageBox.warning(self, "Signup failed", msg)
            return

        user = verify_login(username, password)
        if user:
            save_session(user)
            self.account_created.emit(user)