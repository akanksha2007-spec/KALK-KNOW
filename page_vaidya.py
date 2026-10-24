"""
Kalki Know — Vaidya AI page.
"""

from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QPushButton,
    QScrollArea, QLineEdit, QSizePolicy
)

from vaidya import ask_vaidya
from kk_config import get_deepseek_key
from voice_input import transcribe_from_mic

FOREST      = "#1B4332"
FOREST_DEEP = "#122C21"
MOSS        = "#52796F"
PARCHMENT   = "#FAF7F0"
CARD        = "#FFFFFF"
SAFFRON     = "#D68C45"
TERRACOTTA  = "#B5493B"
INK         = "#22281F"
INK_SOFT    = "#5B6358"
LINE        = "#E4E0D4"
OK          = "#3E7A4C"


class VaidyaWorker(QThread):
    finished = Signal(str, str)

    def __init__(self, question):
        super().__init__()
        self.question = question

    def run(self):
        answer, error = ask_vaidya(self.question)
        self.finished.emit(answer or "", error or "")


class MicWorker(QThread):
    finished = Signal(str, str)  # (text, error)

    def run(self):
        text, error = transcribe_from_mic()
        self.finished.emit(text or "", error or "")


class Bubble(QFrame):
    def __init__(self, text, role="assistant"):
        super().__init__()
        if role == "user":
            bg, fg, border = FOREST, "#FFFFFF", FOREST
        else:
            bg, fg, border = CARD, INK, LINE

        self.setStyleSheet(
            f"QFrame {{ background:{bg}; border:1px solid {border}; border-radius:12px; }}"
        )
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)

        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        lbl.setStyleSheet(f"color:{fg}; font-size:13px; border:none; background:transparent;")
        lbl.setMaximumWidth(560)
        lay.addWidget(lbl)


class Page(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{PARCHMENT};")
        self.worker = None
        self.mic_worker = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(12)

        # Header
        header = QHBoxLayout()
        left = QVBoxLayout()
        eyebrow = QLabel("AI TOOLS")
        eyebrow.setStyleSheet(f"color:{MOSS}; font-size:11.5px; font-weight:600;")
        left.addWidget(eyebrow)
        title = QLabel("Vaidya AI")
        title.setStyleSheet(f"color:{FOREST_DEEP}; font-size:22px; font-weight:700;")
        left.addWidget(title)
        sub = QLabel("Ask anything about medicinal plants, remedies, or traditional uses.")
        sub.setStyleSheet(f"color:{INK_SOFT}; font-size:12.5px;")
        left.addWidget(sub)
        header.addLayout(left)
        header.addStretch()

        has_key = bool(get_deepseek_key())
        status_text = "● Connected to DeepSeek" if has_key else "● API key missing"
        status_color = OK if has_key else TERRACOTTA
        status = QLabel(status_text)
        status.setStyleSheet(
            f"color:{status_color}; font-size:11.5px; font-weight:600; "
            f"background:#FFFFFF; border:1px solid {LINE}; "
            f"padding:6px 12px; border-radius:16px;"
        )
        header.addWidget(status, 0, Qt.AlignTop)
        outer.addLayout(header)

        # Chat area
        chat_frame = QFrame()
        chat_frame.setStyleSheet(
            f"QFrame {{ background:{CARD}; border:1px solid {LINE}; border-radius:12px; }}"
        )
        cf = QVBoxLayout(chat_frame)
        cf.setContentsMargins(16, 16, 16, 16)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.chat_host = QWidget()
        self.chat_host.setStyleSheet(f"background:{CARD};")
        self.chat_layout = QVBoxLayout(self.chat_host)
        self.chat_layout.setContentsMargins(0, 0, 0, 0)
        self.chat_layout.setSpacing(10)
        self.chat_layout.addStretch()

        self.scroll.setWidget(self.chat_host)
        cf.addWidget(self.scroll)
        outer.addWidget(chat_frame, 1)

        # Input row
        input_row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("e.g. What helps with a cough? How do I use Tulsi?")
        self.input.setStyleSheet(f"""
            QLineEdit {{ background:{CARD}; border:1px solid {LINE};
                         border-radius:8px; padding:10px 14px;
                         font-size:13px; color:{INK}; }}
            QLineEdit:focus {{ border-color:{MOSS}; }}
        """)
        self.input.returnPressed.connect(self.send)
        input_row.addWidget(self.input, 1)

        self.mic_btn = QPushButton("🎤")
        self.mic_btn.setFixedWidth(46)
        self.mic_btn.setToolTip("Speak your question (offline)")
        self.mic_btn.setStyleSheet(f"""
            QPushButton {{ background:{CARD}; border:1px solid {LINE};
                           border-radius:8px; padding:10px 8px;
                           font-size:15px; color:{INK}; }}
            QPushButton:hover {{ border-color:{MOSS}; }}
            QPushButton:disabled {{ background:#E4E0D4; color:{INK_SOFT}; }}
        """)
        self.mic_btn.clicked.connect(self.start_listening)
        input_row.addWidget(self.mic_btn)

        self.send_btn = QPushButton("Send")
        self.send_btn.setStyleSheet(f"""
            QPushButton {{ background:{FOREST}; color:white; border:none;
                           border-radius:8px; padding:10px 20px;
                           font-size:13px; font-weight:600; }}
            QPushButton:hover {{ background:#2E5A46; }}
            QPushButton:disabled {{ background:#E4E0D4; color:{INK_SOFT}; }}
        """)
        self.send_btn.clicked.connect(self.send)
        input_row.addWidget(self.send_btn)
        outer.addLayout(input_row)

        # Welcome bubble
        self.add_bubble(
            "Namaste. I'm Vaidya. Ask me about any plant, remedy, or traditional use — "
            "even if you don't know the name. I'll answer in plain language.",
            "assistant",
        )

    def add_bubble(self, text, role):
        b = Bubble(text, role)
        row = QHBoxLayout()
        if role == "user":
            row.addStretch()
            row.addWidget(b)
        else:
            row.addWidget(b)
            row.addStretch()
        wrapper = QWidget()
        wrapper.setStyleSheet(f"background:{CARD};")
        wrapper.setLayout(row)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, wrapper)
        QTimer.singleShot(30, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()
        ))

    def send(self):
        q = self.input.text().strip()
        if not q:
            return
        if self.worker and self.worker.isRunning():
            return

        self.input.clear()
        self.add_bubble(q, "user")
        self.send_btn.setEnabled(False)
        self.send_btn.setText("…")

        self.worker = VaidyaWorker(q)
        self.worker.finished.connect(self.on_reply)
        self.worker.start()

    def on_reply(self, answer, error):
        self.send_btn.setEnabled(True)
        self.send_btn.setText("Send")
        if error:
            self.add_bubble(f"Sorry — something went wrong.\n\n{error}", "assistant")
        else:
            self.add_bubble(answer, "assistant")

    def start_listening(self):
        if self.worker and self.worker.isRunning():
            return
        self.mic_btn.setEnabled(False)
        self.mic_btn.setText("●")
        self.input.setPlaceholderText("Listening… speak now")

        self.mic_worker = MicWorker()
        self.mic_worker.finished.connect(self.on_mic_result)
        self.mic_worker.start()

    def on_mic_result(self, text, error):
        self.mic_btn.setEnabled(True)
        self.mic_btn.setText("🎤")
        self.input.setPlaceholderText("e.g. What helps with a cough? How do I use Tulsi?")

        if error:
            self.add_bubble(f"Voice input unavailable.\n\n{error}", "assistant")
            return
        if text:
            self.input.setText(text)
            self.input.setFocus()