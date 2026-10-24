"""
Kalki Know — the auth window. Hosts either LoginPage or SignupPage.
"""

from PySide6.QtWidgets import QMainWindow, QStackedWidget, QWidget, QVBoxLayout

from page_login import LoginPage
from page_signup import SignupPage

PARCHMENT = "#FAF7F0"


class AuthWindow(QMainWindow):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success
        self.setWindowTitle("Kalki Know — Sign in")
        self.resize(760, 640)
        self.setStyleSheet(f"QMainWindow {{ background:{PARCHMENT}; }}")

        host = QWidget()
        self.setCentralWidget(host)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        self.login_page = LoginPage()
        self.signup_page = SignupPage()
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.signup_page)

        self.login_page.switch_to_signup.connect(self.show_signup)
        self.login_page.logged_in.connect(self._success)

        self.signup_page.switch_to_login.connect(self.show_login)
        self.signup_page.account_created.connect(self._success)

        self.stack.setCurrentWidget(self.login_page)

    def show_login(self):
        self.stack.setCurrentWidget(self.login_page)

    def show_signup(self):
        self.stack.setCurrentWidget(self.signup_page)

    def _success(self, user):
        self.on_success(user)
        self.close()