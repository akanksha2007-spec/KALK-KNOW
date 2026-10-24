"""
Kalki Know — Research Contributions page.
Table + upload modal dialog.
"""

import os
import sys
import shutil
import sqlite3
import subprocess
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame,
    QPushButton, QLineEdit, QComboBox, QTextEdit, QFileDialog,
    QMessageBox, QDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)

from shell import (
    FOREST, FOREST_DEEP, PARCHMENT, CARD, SAFFRON, TERRACOTTA,
    INK, INK_SOFT, LINE
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "kalki.db")
FILES_DIR = os.path.join(BASE_DIR, "research_files")
TABLE = "research_contributions"

TYPES = [
    "Paper", "Preprint", "Thesis",
    "Breakthrough", "Field Note", "Observation"
]


# ------------------------------------------------------------------
# DB
# ------------------------------------------------------------------
def init_db():
    os.makedirs(FILES_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            authors TEXT,
            type TEXT,
            plants TEXT,
            year TEXT,
            abstract TEXT,
            file_path TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def insert_contribution(
    title, authors, ctype, plants, year, abstract, file_path
):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(f"""
        INSERT INTO {TABLE}
        (title, authors, type, plants, year, abstract, file_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        title, authors, ctype, plants, year, abstract, file_path
    ))

    conn.commit()
    conn.close()


def fetch_all(type_filter=None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if type_filter and type_filter != "All":
        cur.execute(
            f"SELECT * FROM {TABLE} WHERE type = ? ORDER BY id DESC",
            (type_filter,)
        )
    else:
        cur.execute(f"SELECT * FROM {TABLE} ORDER BY id DESC")

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def delete_contribution(cid, file_path):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {TABLE} WHERE id = ?", (cid,))
    conn.commit()
    conn.close()

    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass


def truncate_words(text, limit=100):
    if not text:
        return ""

    words = text.split()
    return text if len(words) <= limit else " ".join(words[:limit]) + "…"


# ==================================================================
# Upload dialog (modal)
# ==================================================================
class UploadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Contribute in Research")
        self.setModal(True)
        self.resize(600, 600)
        self.setStyleSheet(f"QDialog {{ background: {CARD}; }}")
        self.selected_file = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 24, 26, 22)
        layout.setSpacing(15)

        header = QHBoxLayout()

        title = QLabel("Contribute in Research")
        title.setStyleSheet(f"""
            color: {FOREST_DEEP};
            font-size: 20px;
            font-weight: 700;
            background: transparent;
        """)
        header.addWidget(title)
        header.addStretch()

        close_btn = QPushButton("×")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setFixedSize(34, 34)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                background: #EDF0E8;
                color: {INK_SOFT};
                font-size: 20px;
                border-radius: 9px;
            }}
            QPushButton:hover {{
                color: {TERRACOTTA};
                background: #F5E5DF;
            }}
        """)
        close_btn.clicked.connect(self.reject)
        header.addWidget(close_btn)
        layout.addLayout(header)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet(f"color: {LINE};")
        layout.addWidget(divider)

        hint = QLabel(
            "Upload your own research paper, thesis, or field observation."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet(f"""
            color: {INK_SOFT};
            font-size: 12px;
            font-style: italic;
            background: transparent;
        """)
        layout.addWidget(hint)

        grid = QGridLayout()
        grid.setHorizontalSpacing(15)
        grid.setVerticalSpacing(12)

        def field(widget, ph=None):
            widget.setStyleSheet(f"""
                QLineEdit, QComboBox, QTextEdit {{
                    background: #FFFEFA;
                    border: 1px solid {LINE};
                    border-radius: 9px;
                    padding: 9px 11px;
                    font-size: 13px;
                    color: {INK};
                }}
                QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{
                    border: 1px solid #789078;
                }}
            """)

            if ph:
                widget.setPlaceholderText(ph)

            return widget

        self.title_in = field(
            QLineEdit(),
            "e.g. Anti-inflammatory effects of Curcuma longa"
        )
        self.authors_in = field(QLineEdit(), "Who is publishing?")
        self.type_in = field(QComboBox())
        self.type_in.addItems(TYPES)
        self.plants_in = field(QLineEdit(), "e.g. Turmeric, Tulsi")
        self.year_in = field(QLineEdit(), str(datetime.now().year))
        self.abstract_in = field(
            QTextEdit(),
            "Short overview (up to ~100 words)…"
        )
        self.abstract_in.setFixedHeight(95)

        def lbl(text):
            label = QLabel(text)
            label.setStyleSheet(f"""
                color: {INK_SOFT};
                font-size: 11.5px;
                font-weight: 600;
                background: transparent;
            """)
            return label

        grid.addWidget(lbl("Title *"), 0, 0)
        grid.addWidget(self.title_in, 0, 1)
        grid.addWidget(lbl("Published by"), 1, 0)
        grid.addWidget(self.authors_in, 1, 1)
        grid.addWidget(lbl("Type"), 2, 0)
        grid.addWidget(self.type_in, 2, 1)
        grid.addWidget(lbl("Year"), 3, 0)
        grid.addWidget(self.year_in, 3, 1)
        grid.addWidget(lbl("Plant(s)"), 4, 0)
        grid.addWidget(self.plants_in, 4, 1)
        grid.addWidget(lbl("Overview"), 5, 0, Qt.AlignTop)
        grid.addWidget(self.abstract_in, 5, 1)

        layout.addLayout(grid)

        file_row = QHBoxLayout()

        file_btn = QPushButton("Attach File")
        file_btn.setCursor(Qt.PointingHandCursor)
        file_btn.setStyleSheet(f"""
            QPushButton {{
                background: #FFFEFA;
                color: {INK};
                border: 1px solid {LINE};
                border-radius: 9px;
                padding: 10px 15px;
                font-size: 12.5px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                border-color: {FOREST};
            }}
        """)
        file_btn.clicked.connect(self.pick_file)
        file_row.addWidget(file_btn)

        self.file_label = QLabel("No file selected")
        self.file_label.setWordWrap(True)
        self.file_label.setStyleSheet(f"""
            color: {INK_SOFT};
            font-size: 11.5px;
            font-style: italic;
            background: transparent;
        """)
        file_row.addWidget(self.file_label, 1)
        layout.addLayout(file_row)

        layout.addStretch()

        footer = QHBoxLayout()
        footer.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: #FFFEFA;
                color: {INK};
                border: 1px solid {LINE};
                border-radius: 9px;
                padding: 10px 19px;
                font-size: 12.5px;
            }}
            QPushButton:hover {{
                border-color: {FOREST};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        footer.addWidget(cancel_btn)

        submit_btn = QPushButton("Submit")
        submit_btn.setCursor(Qt.PointingHandCursor)
        submit_btn.setStyleSheet(f"""
            QPushButton {{
                background: {FOREST};
                color: white;
                border: none;
                border-radius: 9px;
                padding: 10px 22px;
                font-size: 12.5px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background: #193A2D;
            }}
        """)
        submit_btn.clicked.connect(self.submit)
        footer.addWidget(submit_btn)

        layout.addLayout(footer)

    def pick_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Attach file",
            "",
            "Documents (*.pdf *.docx *.doc *.txt *.jpg *.jpeg *.png)"
        )

        if not path:
            return

        self.selected_file = path
        self.file_label.setText(os.path.basename(path))

    def submit(self):
        title = self.title_in.text().strip()

        if not title:
            QMessageBox.warning(
                self,
                "Missing title",
                "Please enter a title."
            )
            return

        saved_path = None

        if self.selected_file:
            base = os.path.basename(self.selected_file)
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
            saved_path = os.path.join(FILES_DIR, stamp + base)

            try:
                shutil.copy2(self.selected_file, saved_path)
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "File error",
                    f"Could not save file:\n{e}"
                )
                saved_path = None

        insert_contribution(
            title,
            self.authors_in.text().strip(),
            self.type_in.currentText(),
            self.plants_in.text().strip(),
            self.year_in.text().strip(),
            self.abstract_in.toPlainText().strip(),
            saved_path,
        )

        self.accept()


# ==================================================================
# Main page
# ==================================================================
class Page(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{PARCHMENT};")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(30, 26, 30, 28)
        outer.setSpacing(17)

        # Header row
        header = QHBoxLayout()
        header_left = QVBoxLayout()
        header_left.setSpacing(5)

        eyebrow = QLabel("TRADITIONAL KNOWLEDGE · RESEARCH")
        eyebrow.setStyleSheet(f"""
            color: #789078;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
            background: transparent;
        """)
        header_left.addWidget(eyebrow)

        title = QLabel("Research Contributions")
        title.setStyleSheet(f"""
            color: {FOREST_DEEP};
            font-size: 25px;
            font-weight: 700;
            background: transparent;
        """)
        header_left.addWidget(title)

        sub = QLabel(
            "Papers, theses, breakthroughs, and field observations "
            "from contributors."
        )
        sub.setWordWrap(True)
        sub.setStyleSheet(f"""
            color: {INK_SOFT};
            font-size: 12.5px;
            background: transparent;
        """)
        header_left.addWidget(sub)

        header.addLayout(header_left, 1)
        header.addStretch()

        upload_btn = QPushButton("＋  Upload Your Research Paper")
        upload_btn.setCursor(Qt.PointingHandCursor)
        upload_btn.setStyleSheet(f"""
            QPushButton {{
                background: {FOREST};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 18px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: #193A2D;
            }}
        """)
        upload_btn.clicked.connect(self.open_upload_dialog)
        header.addWidget(upload_btn, 0, Qt.AlignTop)
        outer.addLayout(header)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        filter_lbl = QLabel("Filter by type:")
        filter_lbl.setStyleSheet(f"""
            color: {INK_SOFT};
            font-size: 12px;
            background: transparent;
        """)
        toolbar.addWidget(filter_lbl)

        self.filter = QComboBox()
        self.filter.addItems(["All"] + TYPES)
        self.filter.setStyleSheet(f"""
            QComboBox {{
                background: {CARD};
                border: 1px solid {LINE};
                border-radius: 9px;
                padding: 8px 12px;
                font-size: 12.5px;
                min-width: 140px;
                color: {INK};
            }}
            QComboBox:focus {{
                border: 1px solid #789078;
            }}
        """)
        self.filter.currentTextChanged.connect(self.refresh_table)
        toolbar.addWidget(self.filter)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background: {CARD};
                color: {INK};
                border: 1px solid {LINE};
                border-radius: 9px;
                padding: 8px 15px;
                font-size: 12.5px;
            }}
            QPushButton:hover {{
                border-color: {FOREST};
            }}
        """)
        refresh_btn.clicked.connect(self.refresh_table)
        toolbar.addWidget(refresh_btn)
        toolbar.addStretch()
        outer.addLayout(toolbar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Title", "Publisher", "Type", "Plant(s)",
            "Date", "Overview", "Actions"
        ])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background: {CARD};
                alternate-background-color: #F8F7F1;
                border: 1px solid {LINE};
                border-radius: 13px;
                font-size: 12.5px;
                color: {INK};
                selection-background-color: #E4ECE5;
                selection-color: {INK};
            }}

            QHeaderView::section {{
                background: #EAEFE5;
                color: {FOREST_DEEP};
                font-size: 11.5px;
                font-weight: 700;
                padding: 12px 10px;
                border: none;
                border-bottom: 1px solid {LINE};
            }}

            QTableWidget::item {{
                padding: 10px;
                border-bottom: 1px solid {LINE};
            }}

            QTableWidget::item:selected {{
                background: #E4ECE5;
                color: {INK};
            }}
        """)

        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.Stretch)
        header_view.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(5, QHeaderView.Stretch)
        header_view.setSectionResizeMode(6, QHeaderView.ResizeToContents)

        self.table.setWordWrap(True)
        outer.addWidget(self.table, 1)

        self.refresh_table()

    def open_upload_dialog(self):
        dlg = UploadDialog(self)

        if dlg.exec() == QDialog.Accepted:
            self.refresh_table()

    def refresh_table(self):
        rows = fetch_all(
            self.filter.currentText()
            if hasattr(self, "filter") else "All"
        )
        self.table.setRowCount(len(rows))

        for r, row in enumerate(rows):
            self.table.setItem(
                r, 0,
                QTableWidgetItem(row["title"] or "(untitled)")
            )
            self.table.setItem(
                r, 1,
                QTableWidgetItem(row["authors"] or "Anonymous")
            )
            self.table.setItem(
                r, 2,
                QTableWidgetItem(row["type"] or "—")
            )
            self.table.setItem(
                r, 3,
                QTableWidgetItem(row["plants"] or "—")
            )

            when = row["submitted_at"] or ""
            if len(when) >= 16:
                when = when[:16]

            self.table.setItem(r, 4, QTableWidgetItem(when))

            overview = truncate_words(row["abstract"] or "", 100)
            self.table.setItem(
                r, 5,
                QTableWidgetItem(overview or "—")
            )

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(6)

            file_path = row["file_path"]

            if file_path and os.path.exists(file_path):
                open_btn = QPushButton("Open")
                open_btn.setCursor(Qt.PointingHandCursor)
                open_btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {CARD};
                        border: 1px solid {LINE};
                        border-radius: 7px;
                        padding: 5px 10px;
                        font-size: 11px;
                        color: {INK};
                    }}
                    QPushButton:hover {{
                        border-color: {FOREST};
                    }}
                """)
                open_btn.clicked.connect(
                    lambda _=False, p=file_path: self.open_file(p)
                )
                actions_layout.addWidget(open_btn)

            del_btn = QPushButton("Delete")
            del_btn.setCursor(Qt.PointingHandCursor)
            del_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {CARD};
                    border: 1px solid {LINE};
                    border-radius: 7px;
                    padding: 5px 10px;
                    font-size: 11px;
                    color: {TERRACOTTA};
                }}
                QPushButton:hover {{
                    border-color: {TERRACOTTA};
                    background: #F8E9E3;
                }}
            """)
            del_btn.clicked.connect(
                lambda _=False, cid=row["id"], fp=file_path:
                self.delete_row(cid, fp)
            )
            actions_layout.addWidget(del_btn)

            self.table.setCellWidget(r, 6, actions_widget)
            self.table.setRowHeight(r, 64)

    def open_file(self, path):
        try:
            if os.name == "nt":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.call(["open", path])
            else:
                subprocess.call(["xdg-open", path])
        except Exception as e:
            QMessageBox.warning(self, "Open failed", str(e))

    def delete_row(self, cid, file_path):
        confirm = QMessageBox.question(
            self,
            "Delete",
            "Delete this contribution?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            delete_contribution(cid, file_path)
            self.refresh_table()


# Ensure table exists as soon as this module is imported.
init_db()