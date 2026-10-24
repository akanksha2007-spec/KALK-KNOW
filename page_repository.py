"""
Kalki Know — Plant Repository page (read-only).
"""

import os
import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame,
    QPushButton, QLineEdit, QScrollArea, QDialog
)

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
OK_SOFT     = "#DCEAD9"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "kalki.db")


def fetch_plants(search=None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if search:
        q = f"%{search.lower()}%"
        cur.execute("""
            SELECT * FROM plants
            WHERE LOWER(common_name) LIKE ?
               OR LOWER(sci_name) LIKE ?
               OR LOWER(family) LIKE ?
               OR LOWER(regional_name) LIKE ?
            ORDER BY common_name COLLATE NOCASE
        """, (q, q, q, q))
    else:
        cur.execute("SELECT * FROM plants ORDER BY common_name COLLATE NOCASE")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_plant(pid):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM plants WHERE id = ?", (pid,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


class PlantDetailDialog(QDialog):
    def __init__(self, plant, parent=None):
        super().__init__(parent)
        self.setWindowTitle(plant.get("common_name") or "Plant")
        self.setModal(True)
        self.resize(640, 720)
        self.setStyleSheet(f"QDialog {{ background: {PARCHMENT}; }}")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 22, 24, 20)
        outer.setSpacing(14)

        # Header
        header = QHBoxLayout()
        left = QVBoxLayout()
        name = QLabel(plant.get("common_name") or "Unknown")
        name.setStyleSheet(f"color:{FOREST_DEEP}; font-size:22px; font-weight:700;")
        left.addWidget(name)
        sci = QLabel(plant.get("sci_name") or "")
        sci.setStyleSheet(f"color:{INK_SOFT}; font-size:13px; font-style:italic;")
        left.addWidget(sci)
        header.addLayout(left)
        header.addStretch()

        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet(f"""
            QPushButton {{ border:none; background:transparent;
                           color:{INK_SOFT}; font-size:20px; }}
            QPushButton:hover {{ color:{TERRACOTTA}; }}
        """)
        close_btn.clicked.connect(self.accept)
        header.addWidget(close_btn, 0, Qt.AlignTop)
        outer.addLayout(header)

        # Image (if exists)
        img_path = plant.get("image_path")
        if img_path and os.path.exists(img_path):
            img_label = QLabel()
            img_label.setAlignment(Qt.AlignCenter)
            pix = QPixmap(img_path)
            if not pix.isNull():
                img_label.setPixmap(pix.scaled(560, 240, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                img_label.setStyleSheet(f"background:#F7F5EE; border:1px solid {LINE}; border-radius:8px; padding:6px;")
                outer.addWidget(img_label)

        # Scrollable details
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        body = QWidget()
        body.setStyleSheet(f"background:{PARCHMENT};")
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(0, 0, 0, 0)
        body_lay.setSpacing(10)

        fields = [
            ("Family", plant.get("family")),
            ("Regional name", plant.get("regional_name")),
            ("Sanskrit name", plant.get("sanskrit_name")),
            ("Plant part used", plant.get("plant_part_used")),
            ("Habitat", plant.get("habitat")),
            ("Native region", plant.get("native_region")),
            ("Conservation status", plant.get("conservation")),
            ("Verification", plant.get("verification")),
            ("Key compounds", plant.get("key_compounds")),
            ("Traditional uses", plant.get("traditional_uses")),
            ("Safety notes", plant.get("safety_notes")),
        ]
        for label, value in fields:
            if not value:
                continue
            block = QFrame()
            block.setStyleSheet(f"QFrame {{ background:{CARD}; border:1px solid {LINE}; border-radius:8px; }}")
            bl = QVBoxLayout(block)
            bl.setContentsMargins(14, 10, 14, 10)
            lbl = QLabel(label.upper())
            lbl.setStyleSheet(f"color:{INK_SOFT}; font-size:10.5px; font-weight:600; letter-spacing:.5px;")
            bl.addWidget(lbl)
            val = QLabel(str(value))
            val.setStyleSheet(f"color:{INK}; font-size:13px;")
            val.setWordWrap(True)
            bl.addWidget(val)
            body_lay.addWidget(block)

        body_lay.addStretch()
        scroll.setWidget(body)
        outer.addWidget(scroll, 1)

        # Footer
        footer = QHBoxLayout()
        footer.addStretch()
        close2 = QPushButton("Close")
        close2.setStyleSheet(f"""
            QPushButton {{ background:white; border:1px solid {LINE};
                           border-radius:7px; padding:9px 18px;
                           font-size:12.5px; color:{INK}; }}
            QPushButton:hover {{ border-color:{FOREST}; }}
        """)
        close2.clicked.connect(self.accept)
        footer.addWidget(close2)
        outer.addLayout(footer)


class Page(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{PARCHMENT};")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 24, 28, 28)
        outer.setSpacing(14)

        # Header
        header = QVBoxLayout()
        eyebrow = QLabel("BOTANICAL DATA")
        eyebrow.setStyleSheet(f"color:{MOSS}; font-size:11.5px; font-weight:600;")
        header.addWidget(eyebrow)
        title = QLabel("Plant Repository")
        title.setStyleSheet(f"color:{FOREST_DEEP}; font-size:22px; font-weight:700;")
        header.addWidget(title)
        self.sub = QLabel("")
        self.sub.setStyleSheet(f"color:{INK_SOFT}; font-size:12.5px;")
        header.addWidget(self.sub)
        outer.addLayout(header)

        # Search
        search_row = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search by common, scientific, family, or regional name…")
        self.search.setStyleSheet(f"""
            QLineEdit {{ background:{CARD}; border:1px solid {LINE};
                         border-radius:8px; padding:10px 14px;
                         font-size:13px; color:{INK}; }}
            QLineEdit:focus {{ border-color:{MOSS}; }}
        """)
        self.search.textChanged.connect(self.refresh)
        search_row.addWidget(self.search, 1)
        outer.addLayout(search_row)

        # Scroll area for the plant cards
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.host = QWidget()
        self.host.setStyleSheet(f"background:{PARCHMENT};")
        self.grid = QGridLayout(self.host)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(14)
        self.scroll.setWidget(self.host)
        outer.addWidget(self.scroll, 1)

        self.refresh()

    def refresh(self):
        # clear
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        search = self.search.text().strip() if hasattr(self, "search") else ""
        rows = fetch_plants(search if search else None)
        self.sub.setText(f"{len(rows)} plant{'s' if len(rows) != 1 else ''} in local database")

        if not rows:
            empty = QLabel("No plants match your search.")
            empty.setStyleSheet(f"color:{INK_SOFT}; font-size:13px; font-style:italic; padding:20px;")
            self.grid.addWidget(empty, 0, 0)
            return

        cols = 3
        for i, p in enumerate(rows):
            card = self._plant_card(p)
            self.grid.addWidget(card, i // cols, i % cols)

        # stretch last row
        last_row = (len(rows) - 1) // cols
        self.grid.setRowStretch(last_row + 1, 1)

    def _plant_card(self, p):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{ background:{CARD}; border:1px solid {LINE}; border-radius:10px; }}
            QFrame:hover {{ border-color:{MOSS}; }}
        """)
        card.setCursor(Qt.PointingHandCursor)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(16, 14, 16, 14)
        cl.setSpacing(8)

        name = QLabel(p.get("common_name") or "Unknown")
        name.setStyleSheet(f"color:{FOREST_DEEP}; font-size:15px; font-weight:700;")
        name.setWordWrap(True)
        cl.addWidget(name)

        sci = QLabel(p.get("sci_name") or "")
        sci.setStyleSheet(f"color:{INK_SOFT}; font-size:11.5px; font-style:italic;")
        sci.setWordWrap(True)
        cl.addWidget(sci)

        family = QLabel(p.get("family") or "—")
        family.setStyleSheet(f"color:{INK_SOFT}; font-size:11.5px;")
        cl.addWidget(family)

        # tags row
        tags = QHBoxLayout()
        tags.setSpacing(6)
        cons = p.get("conservation")
        if cons:
            color = OK if "Least" in cons else (SAFFRON if "Near" in cons or "Vulnerable" in cons else TERRACOTTA)
            bg = OK_SOFT if "Least" in cons else "#F3DCC0"
            tag = QLabel(cons)
            tag.setStyleSheet(f"background:{bg}; color:{color}; font-size:10px; font-weight:600; padding:2px 8px; border-radius:10px;")
            tags.addWidget(tag)
        verif = p.get("verification")
        if verif:
            v_color = OK if verif == "Verified" else SAFFRON
            v_bg = OK_SOFT if verif == "Verified" else "#F3DCC0"
            vt = QLabel(verif)
            vt.setStyleSheet(f"background:{v_bg}; color:{v_color}; font-size:10px; font-weight:600; padding:2px 8px; border-radius:10px;")
            tags.addWidget(vt)
        tags.addStretch()
        cl.addLayout(tags)

        cl.addStretch()

        view_btn = QPushButton("View details →")
        view_btn.setStyleSheet(f"""
            QPushButton {{ background:transparent; border:none; color:{MOSS};
                           font-size:12px; font-weight:600; padding:4px 0; text-align:left; }}
            QPushButton:hover {{ color:{FOREST_DEEP}; }}
        """)
        view_btn.clicked.connect(lambda _=False, pid=p["id"]: self.open_detail(pid))
        cl.addWidget(view_btn)

        # make whole card clickable too
        card.mousePressEvent = lambda e, pid=p["id"]: self.open_detail(pid)
        return card

    def open_detail(self, pid):
        plant = get_plant(pid)
        if not plant:
            return
        dlg = PlantDetailDialog(plant, self)
        dlg.exec()