"""
Kalki Know — User Settings page.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame,
    QPushButton, QLineEdit, QComboBox, QMessageBox
)

from auth import update_user, ROLES, load_session, clear_session

FOREST      = "#244D39"
FOREST_DEEP = "#203128"
PARCHMENT   = "#F5F2E9"
CARD        = "#FFFEFA"
SAFFRON     = "#C5A15A"
TERRACOTTA  = "#B9654D"
INK         = "#203128"
INK_SOFT    = "#68776B"
LINE        = "#E4DFD2"
MOSS        = "#789078"


class Page(QWidget):
    logged_out = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{PARCHMENT};")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(30, 26, 30, 28)
        outer.setSpacing(17)

        title = QLabel("User Settings")
        title.setStyleSheet(f"""
            color: {FOREST_DEEP};
            font-size: 25px;
            font-weight: 700;
            background: transparent;
        """)
        outer.addWidget(title)

        sub = QLabel("Manage your profile, role, and password.")
        sub.setStyleSheet(f"""
            color: {INK_SOFT};
            font-size: 13px;
            background: transparent;
        """)
        outer.addWidget(sub)

        # Profile card
        profile = QFrame()
        profile.setObjectName("ProfileCard")
        profile.setStyleSheet(f"""
            QFrame#ProfileCard {{
                background: {CARD};
                border: 1px solid {LINE};
                border-radius: 15px;
            }}
        """)

        pl = QVBoxLayout(profile)
        pl.setContentsMargins(25, 23, 25, 23)
        pl.setSpacing(13)

        self.username_label = QLabel("—")
        self.username_label.setStyleSheet(f"""
            color: {FOREST_DEEP};
            font-size: 19px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        pl.addWidget(self.username_label)

        self.meta_label = QLabel("")
        self.meta_label.setStyleSheet(f"""
            color: {INK_SOFT};
            font-size: 12px;
            background: transparent;
            border: none;
        """)
        pl.addWidget(self.meta_label)

        pl.addSpacing(7)

        hdr = QLabel("Update profile")
        hdr.setStyleSheet(f"""
            color: {FOREST_DEEP};
            font-size: 16px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        pl.addWidget(hdr)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(13)

        def lbl(text):
            label = QLabel(text)
            label.setStyleSheet(f"""
                color: {INK_SOFT};
                font-size: 12px;
                font-weight: 600;
                background: transparent;
                border: none;
            """)
            return label

        def styled(widget):
            widget.setMinimumHeight(41)
            widget.setStyleSheet(f"""
                QLineEdit, QComboBox {{
                    background: {CARD};
                    border: 1px solid {LINE};
                    border-radius: 9px;
                    padding: 9px 11px;
                    font-size: 13px;
                    color: {INK};
                }}
                QLineEdit:focus, QComboBox:focus {{
                    border: 1px solid {MOSS};
                }}
            """)
            return widget

        self.email_in = styled(QLineEdit())

        self.role_in = styled(QComboBox())
        for r in ROLES:
            self.role_in.addItem(r)

        self.password_in = styled(QLineEdit())
        self.password_in.setEchoMode(QLineEdit.Password)
        self.password_in.setPlaceholderText(
            "Leave blank to keep current"
        )

        grid.addWidget(lbl("Email"), 0, 0)
        grid.addWidget(self.email_in, 0, 1)
        grid.addWidget(lbl("Role"), 1, 0)
        grid.addWidget(self.role_in, 1, 1)
        grid.addWidget(lbl("New password"), 2, 0)
        grid.addWidget(self.password_in, 2, 1)

        pl.addLayout(grid)

        save_btn = QPushButton("Save changes")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setMinimumHeight(42)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {FOREST};
                color: white;
                border: none;
                border-radius: 9px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: #193A2D;
            }}
        """)
        save_btn.clicked.connect(self.save_changes)
        pl.addWidget(save_btn, alignment=Qt.AlignLeft)

        outer.addWidget(profile)

        # Logout card
        logout_card = QFrame()
        logout_card.setObjectName("LogoutCard")
        logout_card.setStyleSheet(f"""
            QFrame#LogoutCard {{
                background: {CARD};
                border: 1px solid {LINE};
                border-radius: 15px;
            }}
        """)

        lc = QHBoxLayout(logout_card)
        lc.setContentsMargins(24, 21, 24, 21)
        lc.setSpacing(15)

        info = QVBoxLayout()
        info.setSpacing(6)

        l_t = QLabel("Log out")
        l_t.setStyleSheet(f"""
            color: {FOREST_DEEP};
            font-size: 15px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        info.addWidget(l_t)

        l_s = QLabel(
            "End your session on this device. "
            "You'll need to log in next time."
        )
        l_s.setWordWrap(True)
        l_s.setStyleSheet(f"""
            color: {INK_SOFT};
            font-size: 12px;
            background: transparent;
            border: none;
        """)
        info.addWidget(l_s)

        lc.addLayout(info, 1)
        lc.addStretch()

        logout_btn = QPushButton("Log out")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setMinimumHeight(41)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background: #FFFEFA;
                color: {TERRACOTTA};
                border: 1px solid {TERRACOTTA};
                border-radius: 9px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {TERRACOTTA};
                color: white;
            }}
        """)
        logout_btn.clicked.connect(self.do_logout)
        lc.addWidget(logout_btn)

        outer.addWidget(logout_card)
        outer.addStretch()

        self.load_user()

    def load_user(self):
        session = load_session()

        if not session:
            return

        self.username_label.setText(session.get("username", ""))
        self.meta_label.setText(
            f"{session.get('email', '')} · "
            f"{session.get('role', '')}"
        )
        self.email_in.setText(session.get("email", ""))

        idx = self.role_in.findText(session.get("role", ""))

        if idx >= 0:
            self.role_in.setCurrentIndex(idx)

    def save_changes(self):
        session = load_session()

        if not session:
            return

        email = self.email_in.text().strip()
        role = self.role_in.currentText()
        pwd = self.password_in.text()

        update_user(
            session["id"],
            email=email,
            role=role,
            password=pwd if pwd else None
        )

        # Keep session in sync
        session["email"] = email
        session["role"] = role

        from auth import save_session
        save_session(session)

        self.password_in.clear()
        self.load_user()

        QMessageBox.information(
            self,
            "Saved",
            "Your settings have been updated."
        )

    def do_logout(self):
        confirm = QMessageBox.question(
            self,
            "Log out",
            "Log out of Kalki Know?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm != QMessageBox.Yes:
            return

        clear_session()
        self.logged_out.emit()