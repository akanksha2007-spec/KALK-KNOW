"""
Kalki Know — Plant Knowledge System
Premium botanical application shell.
"""

import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QColor, QPainter, QLinearGradient
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QFrame, QPushButton, QStackedWidget
)

# ---------------- PREMIUM BOTANICAL PALETTE ----------------
# Keep these variable names unchanged.

SIDEBAR_BG   = "#193A2D"
SIDEBAR_TXT  = "#EAF0E5"
SIDEBAR_ACT  = "#315844"
SIDEBAR_LINE = "#355744"

CREAM        = "#F5F2E9"
CARD         = "#FFFEFA"
GOLD         = "#C5A15A"
GOLD_SOFT    = "#F3E8CC"
INK          = "#203128"
INK_SOFT     = "#68776B"
LINE         = "#E4DFD2"
OK           = "#427653"
OK_SOFT      = "#E3EEE0"
TERRACOTTA   = "#B9654D"

# Aliases used by the other pages.
FOREST        = "#244D39"
FOREST_DEEP   = INK
MOSS          = "#789078"
PARCHMENT     = CREAM
SAFFRON       = GOLD
SAFFRON_SOFT  = GOLD_SOFT

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "kalki.db")
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")

PAGES = [
    ("dashboard",  "Dashboard",              "page_dashboard",      "Page"),
    ("identify",   "Plant Identification",   "page_identification", "Page"),
    ("repository", "Plant Repository",       "page_repository",     "Page"),
    ("remedies",   "Herbal Remedies",        "page_remedies",       "Page"),
    ("vaidya",     "Vaidya AI",              "page_vaidya",         "Page"),
    ("research",   "Research Contributions", "page_research",       "Page"),
    ("settings",   "User Settings",          "page_settings",       "Page"),
]


class OmbreWidget(QWidget):
    """Soft cream background for the main application area."""

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor("#F9F7F0"))
        gradient.setColorAt(0.55, QColor("#F5F2E9"))
        gradient.setColorAt(1.0, QColor("#EFEBDD"))

        painter.fillRect(self.rect(), gradient)


class Shell(QMainWindow):
    def __init__(self, user=None):
        super().__init__()

        self.user = user or {}
        self.setWindowTitle("Kalki Know — Plant Knowledge System")
        self.resize(1360, 850)
        self.setMinimumSize(1000, 650)

        self.setStyleSheet(f"""
            QWidget {{
                font-family: "Segoe UI";
                color: {INK};
            }}

            QToolTip {{
                background: {SIDEBAR_BG};
                color: #FFFFFF;
                border: 1px solid {GOLD};
                border-radius: 6px;
                padding: 6px 8px;
            }}

            QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {{
                background: {CARD};
                color: {INK};
                border: 1px solid {LINE};
                border-radius: 9px;
                padding: 8px 10px;
                selection-background-color: {FOREST};
                selection-color: #FFFFFF;
            }}

            QLineEdit:focus, QTextEdit:focus,
            QPlainTextEdit:focus, QComboBox:focus {{
                border: 1px solid {MOSS};
            }}

            QCheckBox {{
                color: {INK};
                spacing: 8px;
            }}

            QScrollBar:vertical {{
                background: transparent;
                width: 10px;
                margin: 3px;
            }}

            QScrollBar::handle:vertical {{
                background: #C9D2C3;
                min-height: 25px;
                border-radius: 5px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: {MOSS};
            }}

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0;
            }}

            QScrollBar:horizontal {{
                background: transparent;
                height: 10px;
                margin: 3px;
            }}

            QScrollBar::handle:horizontal {{
                background: #C9D2C3;
                min-width: 25px;
                border-radius: 5px;
            }}

            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {{
                width: 0;
            }}
        """)

        root = QWidget()
        self.setCentralWidget(root)

        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ---------------- SIDEBAR ----------------
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(250)
        self.sidebar.setStyleSheet(f"""
            QFrame {{
                background: {SIDEBAR_BG};
                border-right: 1px solid {SIDEBAR_LINE};
            }}
        """)

        side_layout = QVBoxLayout(self.sidebar)
        side_layout.setContentsMargins(15, 20, 15, 20)
        side_layout.setSpacing(7)

        # ---------------- LOGO ----------------
        self.logo_btn = QPushButton()
        self.logo_btn.setCursor(Qt.PointingHandCursor)
        self.logo_btn.setFlat(True)
        self.logo_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                padding: 4px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 10px;
            }
        """)
        self.logo_btn.clicked.connect(lambda: self.goto("dashboard"))

        if os.path.exists(LOGO_PATH):
            pix = QPixmap(LOGO_PATH)

            if not pix.isNull():
                scaled = pix.scaled(
                    210,
                    150,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.logo_btn.setIcon(scaled)
                self.logo_btn.setIconSize(scaled.size())
                self.logo_btn.setFixedHeight(scaled.height() + 12)

        side_layout.addWidget(self.logo_btn, alignment=Qt.AlignCenter)

        spacer = QWidget()
        spacer.setFixedHeight(14)
        side_layout.addWidget(spacer)

        # ---------------- NAVIGATION ----------------
        self.nav_buttons = {}

        for key, label, _mod, _cls in PAGES:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumHeight(42)
            btn.setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding: 10px 13px;
                    color: {SIDEBAR_TXT};
                    background: transparent;
                    border: 1px solid transparent;
                    border-radius: 9px;
                    font-size: 13px;
                    font-weight: 500;
                }}

                QPushButton:hover {{
                    background: {SIDEBAR_ACT};
                    border: 1px solid #41674F;
                }}

                QPushButton:checked {{
                    background: #E6ECDD;
                    color: {SIDEBAR_BG};
                    border: 1px solid #D5E0CF;
                    font-weight: 700;
                }}
            """)

            btn.clicked.connect(lambda _=False, k=key: self.goto(k))
            side_layout.addWidget(btn)
            self.nav_buttons[key] = btn

        side_layout.addStretch()

        # ---------------- USER INFO ----------------
        who = self.user.get("username", "guest")

        user_lbl = QLabel(f"Signed in as\n{who}")
        user_lbl.setWordWrap(True)
        user_lbl.setStyleSheet(f"""
            color: #D3DFD1;
            font-size: 11px;
            border: none;
            padding: 8px 4px;
        """)
        side_layout.addWidget(user_lbl)

        mode = QLabel("●  Offline · SQLite")
        mode.setStyleSheet("""
            QLabel {
                color: #E2EADD;
                font-size: 11px;
                background: #294B38;
                padding: 10px;
                border-radius: 9px;
                border: 1px solid #3B6048;
            }
        """)
        side_layout.addWidget(mode)

        layout.addWidget(self.sidebar)

        # ---------------- MAIN AREA ----------------
        self.main_area = OmbreWidget()

        main_layout = QVBoxLayout(self.main_area)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.host = QStackedWidget()
        self.host.setStyleSheet("""
            QStackedWidget {
                background: transparent;
                border: none;
            }
        """)

        main_layout.addWidget(self.host)
        layout.addWidget(self.main_area, 1)

        self.current_page = None
        self.current_key = None

        self.goto("dashboard")

    def goto(self, key):
        if key == self.current_key:
            return

        if self.current_page is not None:
            self.host.removeWidget(self.current_page)
            self.current_page.deleteLater()
            self.current_page = None

        page_conf = next((p for p in PAGES if p[0] == key), None)

        if not page_conf:
            return

        _, label, mod_name, cls_name = page_conf

        if mod_name is None:
            page = self._placeholder(label)
        else:
            try:
                mod = __import__(mod_name, fromlist=[cls_name])
                cls = getattr(mod, cls_name)
                page = cls(self)

                if hasattr(page, "logged_out"):
                    page.logged_out.connect(self.handle_logout)

            except Exception as e:
                page = self._error_page(label, mod_name, e)

        self.host.addWidget(page)
        self.host.setCurrentWidget(page)

        self.current_page = page
        self.current_key = key

        for k, btn in self.nav_buttons.items():
            btn.setChecked(k == key)

    def handle_logout(self):
        from auth_window import AuthWindow
        from main import launch_shell

        self.close()
        self.auth = AuthWindow(on_success=launch_shell)
        self.auth.show()

    def _placeholder(self, label):
        w = QWidget()
        w.setStyleSheet("background: transparent;")

        lay = QVBoxLayout(w)
        lay.setContentsMargins(40, 40, 40, 40)

        t = QLabel(label)
        t.setStyleSheet(
            f"color:{INK}; font-size:24px; font-weight:700;"
        )
        lay.addWidget(t)

        s = QLabel("This page is coming soon.")
        s.setStyleSheet(
            f"color:{INK_SOFT}; font-size:13px; padding-top:6px;"
        )
        lay.addWidget(s)
        lay.addStretch()

        return w

    def _error_page(self, label, mod_name, error):
        w = QWidget()
        w.setStyleSheet("background: transparent;")

        lay = QVBoxLayout(w)
        lay.setContentsMargins(40, 40, 40, 40)

        t = QLabel(f"{label} failed to load")
        t.setStyleSheet(
            f"color:{TERRACOTTA}; font-size:20px; font-weight:700;"
        )
        lay.addWidget(t)

        s = QLabel(f"Could not import {mod_name}.py\n\n{error}")
        s.setStyleSheet(
            f"color:{INK_SOFT}; font-size:12px; padding-top:6px;"
        )
        s.setWordWrap(True)
        lay.addWidget(s)
        lay.addStretch()

        return w