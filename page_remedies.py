"""
Kalki Know — Herbal Remedies page.
"""

import os
import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame,
    QPushButton, QLineEdit, QScrollArea, QDialog, QSizePolicy
)

FOREST      = "#244D39"
FOREST_DEEP = "#203128"
MOSS        = "#789078"
PARCHMENT   = "#F5F2E9"
CARD        = "#FFFEFA"
SAFFRON     = "#C5A15A"
TERRACOTTA  = "#B9654D"
INK         = "#203128"
INK_SOFT    = "#68776B"
LINE        = "#E4DFD2"
OK          = "#427653"
BLUE_SOFT   = "#E4ECE5"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "kalki.db")


def fetch_remedies(search=None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if search:
        q = f"%{search.lower()}%"
        cur.execute("""
            SELECT * FROM remedies
            WHERE LOWER(disease) LIKE ?
               OR LOWER(plant_common_name) LIKE ?
               OR LOWER(sci_name) LIKE ?
               OR LOWER(therapeutic_use) LIKE ?
            ORDER BY disease COLLATE NOCASE
        """, (q, q, q, q))
    else:
        cur.execute(
            "SELECT * FROM remedies ORDER BY disease COLLATE NOCASE"
        )

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


class RemedyDetailDialog(QDialog):
    def __init__(self, remedy, parent=None):
        super().__init__(parent)

        self.setWindowTitle(remedy.get("disease") or "Remedy")
        self.setModal(True)
        self.resize(600, 640)
        self.setStyleSheet(f"QDialog {{ background: {PARCHMENT}; }}")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(25, 24, 25, 22)
        outer.setSpacing(15)

        header = QHBoxLayout()
        left = QVBoxLayout()
        left.setSpacing(5)

        title = QLabel(remedy.get("plant_common_name") or "Remedy")
        title.setWordWrap(True)
        title.setStyleSheet(f"""
            color: {FOREST_DEEP};
            font-size: 23px;
            font-weight: 700;
            background: transparent;
        """)
        left.addWidget(title)

        sci = QLabel(remedy.get("sci_name") or "")
        sci.setStyleSheet(f"""
            color: {INK_SOFT};
            font-size: 13px;
            font-style: italic;
            background: transparent;
        """)
        left.addWidget(sci)

        header.addLayout(left, 1)
        header.addStretch()

        close_btn = QPushButton("×")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setFixedSize(34, 34)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                background: #EBEEE5;
                color: {INK_SOFT};
                font-size: 21px;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background: #F5E5DF;
                color: {TERRACOTTA};
            }}
        """)
        close_btn.clicked.connect(self.accept)
        header.addWidget(close_btn, 0, Qt.AlignTop)
        outer.addLayout(header)

        for_lbl = QLabel(f"For: {remedy.get('disease', '')}")
        for_lbl.setStyleSheet(f"""
            background: {BLUE_SOFT};
            color: {FOREST};
            font-size: 12px;
            font-weight: 600;
            padding: 7px 12px;
            border-radius: 9px;
        """)
        for_lbl.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        outer.addWidget(for_lbl, 0, Qt.AlignLeft)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)

        body = QWidget()
        body.setStyleSheet("background: transparent;")

        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(0, 0, 0, 0)
        body_lay.setSpacing(10)

        fields = [
            ("Plant part used", remedy.get("plant_part")),
            ("Therapeutic use", remedy.get("therapeutic_use")),
            ("Preparation", remedy.get("preparation")),
            ("Dosage form", remedy.get("dosage_form")),
            ("Phytochemical", remedy.get("phytochemical")),
            ("Usage notes", remedy.get("usage_notes")),
        ]

        for label, value in fields:
            if not value:
                continue

            block = QFrame()
            block.setStyleSheet(f"""
                QFrame {{
                    background: {CARD};
                    border: 1px solid {LINE};
                    border-radius: 11px;
                }}
            """)

            bl = QVBoxLayout(block)
            bl.setContentsMargins(15, 12, 15, 12)
            bl.setSpacing(6)

            lbl = QLabel(label.upper())
            lbl.setStyleSheet(f"""
                color: {INK_SOFT};
                font-size: 10.5px;
                font-weight: 700;
                letter-spacing: 0.6px;
                background: transparent;
                border: none;
            """)
            bl.addWidget(lbl)

            val = QLabel(str(value))
            val.setStyleSheet(f"""
                color: {INK};
                font-size: 13px;
                background: transparent;
                border: none;
            """)
            val.setWordWrap(True)
            bl.addWidget(val)

            body_lay.addWidget(block)

        body_lay.addStretch()
        scroll.setWidget(body)
        outer.addWidget(scroll, 1)

        footer = QHBoxLayout()
        footer.addStretch()

        close2 = QPushButton("Close")
        close2.setCursor(Qt.PointingHandCursor)
        close2.setStyleSheet(f"""
            QPushButton {{
                background: {FOREST};
                border: none;
                border-radius: 9px;
                padding: 10px 22px;
                font-size: 12.5px;
                font-weight: 600;
                color: #FFFFFF;
            }}
            QPushButton:hover {{
                background: #193A2D;
            }}
        """)
        close2.clicked.connect(self.accept)
        footer.addWidget(close2)
        outer.addLayout(footer)


class Page(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{PARCHMENT};")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(30, 26, 30, 28)
        outer.setSpacing(17)

        header = QVBoxLayout()
        header.setSpacing(5)

        eyebrow = QLabel("TRADITIONAL KNOWLEDGE")
        eyebrow.setStyleSheet(f"""
            color: {MOSS};
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1.2px;
            background: transparent;
        """)
        header.addWidget(eyebrow)

        title = QLabel("Herbal Remedies")
        title.setStyleSheet(f"""
            color: {FOREST_DEEP};
            font-size: 25px;
            font-weight: 700;
            background: transparent;
        """)
        header.addWidget(title)

        self.sub = QLabel("")
        self.sub.setStyleSheet(f"""
            color: {INK_SOFT};
            font-size: 12.5px;
            background: transparent;
        """)
        header.addWidget(self.sub)
        outer.addLayout(header)

        search_row = QHBoxLayout()

        self.search = QLineEdit()
        self.search.setPlaceholderText(
            "Search by disease, plant, or use…"
        )
        self.search.setMinimumHeight(43)
        self.search.setStyleSheet(f"""
            QLineEdit {{
                background: {CARD};
                border: 1px solid {LINE};
                border-radius: 10px;
                padding: 10px 14px;
                font-size: 13px;
                color: {INK};
            }}
            QLineEdit:focus {{
                border: 1px solid {MOSS};
            }}
        """)
        self.search.textChanged.connect(self.refresh)
        search_row.addWidget(self.search, 1)
        outer.addLayout(search_row)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)

        self.host = QWidget()
        self.host.setStyleSheet("background: transparent;")

        self.list_layout = QVBoxLayout(self.host)
        self.list_layout.setContentsMargins(0, 0, 4, 0)
        self.list_layout.setSpacing(13)
        self.list_layout.addStretch()

        self.scroll.setWidget(self.host)
        outer.addWidget(self.scroll, 1)

        self.refresh()

    def refresh(self):
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        search = self.search.text().strip() if hasattr(self, "search") else ""
        rows = fetch_remedies(search if search else None)

        self.sub.setText(
            f"{len(rows)} remed{'ies' if len(rows) != 1 else 'y'} "
            "in local database"
        )

        if not rows:
            empty = QLabel("No remedies match your search.")
            empty.setStyleSheet(f"""
                color: {INK_SOFT};
                font-size: 13px;
                font-style: italic;
                padding: 20px;
                background: {CARD};
                border: 1px solid {LINE};
                border-radius: 12px;
            """)
            self.list_layout.insertWidget(0, empty)
            return

        for r in rows:
            card = self._remedy_card(r)
            self.list_layout.insertWidget(
                self.list_layout.count() - 1,
                card
            )

    def _remedy_card(self, r):
        card = QFrame()
        card.setObjectName("RemedyCard")
        card.setStyleSheet(f"""
            QFrame#RemedyCard {{
                background: {CARD};
                border: 1px solid {LINE};
                border-radius: 14px;
            }}
            QFrame#RemedyCard:hover {{
                border: 1px solid {MOSS};
            }}
        """)
        card.setCursor(Qt.PointingHandCursor)

        cl = QVBoxLayout(card)
        cl.setContentsMargins(19, 16, 19, 16)
        cl.setSpacing(8)

        top = QHBoxLayout()
        top.setSpacing(10)

        plant = QLabel(r.get("plant_common_name") or "Unknown")
        plant.setWordWrap(True)
        plant.setStyleSheet(f"""
            color: {FOREST_DEEP};
            font-size: 16px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        top.addWidget(plant, 1)

        disease = QLabel(r.get("disease") or "")
        disease.setWordWrap(True)
        disease.setStyleSheet(f"""
            background: {BLUE_SOFT};
            color: {FOREST};
            font-size: 10.5px;
            font-weight: 600;
            padding: 5px 9px;
            border-radius: 8px;
            border: none;
        """)
        top.addWidget(disease, 0, Qt.AlignTop)
        cl.addLayout(top)

        sci = QLabel(r.get("sci_name") or "")
        sci.setStyleSheet(f"""
            color: {INK_SOFT};
            font-size: 11.5px;
            font-style: italic;
            background: transparent;
            border: none;
        """)
        cl.addWidget(sci)

        if r.get("therapeutic_use"):
            use = QLabel(r["therapeutic_use"])
            use.setStyleSheet(f"""
                color: {INK};
                font-size: 13px;
                margin-top: 4px;
                background: transparent;
                border: none;
            """)
            use.setWordWrap(True)
            cl.addWidget(use)

        meta_bits = []

        if r.get("plant_part"):
            meta_bits.append(f"Part: {r['plant_part']}")

        if r.get("dosage_form"):
            meta_bits.append(f"Form: {r['dosage_form']}")

        if meta_bits:
            meta = QLabel("  ·  ".join(meta_bits))
            meta.setWordWrap(True)
            meta.setStyleSheet(f"""
                color: {INK_SOFT};
                font-size: 11.5px;
                background: transparent;
                border: none;
            """)
            cl.addWidget(meta)

        view = QPushButton("View full remedy  →")
        view.setCursor(Qt.PointingHandCursor)
        view.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {FOREST};
                font-size: 12px;
                font-weight: 700;
                padding: 5px 0;
                text-align: left;
            }}
            QPushButton:hover {{
                color: {MOSS};
            }}
        """)
        view.clicked.connect(
            lambda _=False, rid=r["id"]: self.open_detail(rid)
        )
        cl.addWidget(view)

        card.mousePressEvent = lambda e, rid=r["id"]: self.open_detail(rid)
        return card

    def open_detail(self, rid):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM remedies WHERE id = ?", (rid,))
        row = cur.fetchone()
        conn.close()

        if not row:
            return

        dlg = RemedyDetailDialog(dict(row), self)
        dlg.exec()