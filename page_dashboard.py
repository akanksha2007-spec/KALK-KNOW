"""
Kalki Know — Dashboard page.
"""

import sqlite3
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame,
    QPushButton, QSizePolicy
)

from shell import (
    FOREST, FOREST_DEEP, MOSS, PARCHMENT, CARD, SAFFRON,
    INK, INK_SOFT, LINE, OK, OK_SOFT
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "kalki.db")
PLANTS_TABLE = "plants"


def get_counts():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {PLANTS_TABLE}")
    total = cur.fetchone()[0]
    cur.execute(
        f"SELECT COUNT(*) FROM {PLANTS_TABLE} "
        "WHERE verification = 'Verified'"
    )
    verified = cur.fetchone()[0]
    cur.execute(
        f"SELECT COUNT(*) FROM {PLANTS_TABLE} "
        "WHERE verification = 'Pending Review'"
    )
    pending = cur.fetchone()[0]
    conn.close()
    return {
        "total": total,
        "verified": verified,
        "pending": pending
    }


def get_recent_plants(limit=5):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(f"""
        SELECT sci_name, common_name, verification
        FROM {PLANTS_TABLE}
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


class StatCard(QFrame):
    def __init__(self, label, value, subtitle, accent):
        super().__init__()

        self.setObjectName("StatCard")
        self.setMinimumHeight(145)
        self.setStyleSheet(f"""
            QFrame#StatCard {{
                background: {CARD};
                border: 1px solid {LINE};
                border-radius: 14px;
            }}
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 17, 18, 17)
        outer.setSpacing(9)

        top = QHBoxLayout()

        lbl = QLabel(label)
        lbl.setWordWrap(True)
        lbl.setStyleSheet(f"""
            color: {INK_SOFT};
            font-size: 12px;
            border: none;
            background: transparent;
        """)
        top.addWidget(lbl, 1)

        icon = QLabel("●")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedSize(34, 34)
        icon.setStyleSheet(f"""
            background: {accent}22;
            color: {accent};
            border-radius: 10px;
            font-size: 13px;
            border: none;
        """)
        top.addWidget(icon, 0, Qt.AlignTop)

        outer.addLayout(top)

        self.value_lbl = QLabel(str(value))
        self.value_lbl.setStyleSheet(f"""
            color: {FOREST_DEEP};
            font-size: 29px;
            font-weight: 700;
            border: none;
            background: transparent;
        """)
        outer.addWidget(self.value_lbl)

        sub = QLabel(subtitle)
        sub.setWordWrap(True)
        sub.setStyleSheet(f"""
            color: {OK};
            background: {OK_SOFT};
            font-size: 11px;
            font-weight: 600;
            padding: 5px 9px;
            border-radius: 9px;
            border: none;
        """)
        sub.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        outer.addWidget(sub)


class Page(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(30, 26, 30, 30)
        outer.setSpacing(20)

        header = QHBoxLayout()

        title = QLabel("Plant Identification Dashboard")
        title.setStyleSheet(f"""
            color: {FOREST_DEEP};
            font-size: 24px;
            font-weight: 700;
            background: transparent;
        """)
        header.addWidget(title)
        header.addStretch()

        refresh = QPushButton("Refresh")
        refresh.setCursor(Qt.PointingHandCursor)
        refresh.setMinimumHeight(40)
        refresh.setStyleSheet(f"""
            QPushButton {{
                background: {FOREST};
                color: #FFFFFF;
                border: none;
                border-radius: 9px;
                padding: 9px 18px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: #193A2D;
            }}
            QPushButton:pressed {{
                background: #102B20;
            }}
        """)
        refresh.clicked.connect(self.refresh)
        header.addWidget(refresh)
        outer.addLayout(header)

        self.kpi_grid = QGridLayout()
        self.kpi_grid.setHorizontalSpacing(15)
        self.kpi_grid.setVerticalSpacing(15)
        outer.addLayout(self.kpi_grid)

        recent_title = QLabel("Recently Added Plants")
        recent_title.setStyleSheet(f"""
            color: {FOREST_DEEP};
            font-size: 17px;
            font-weight: 700;
            padding-top: 5px;
            background: transparent;
        """)
        outer.addWidget(recent_title)

        self.recent_frame = QFrame()
        self.recent_frame.setObjectName("RecentPlantsCard")
        self.recent_frame.setStyleSheet(f"""
            QFrame#RecentPlantsCard {{
                background: {CARD};
                border: 1px solid {LINE};
                border-radius: 14px;
            }}
        """)

        self.recent_layout = QVBoxLayout(self.recent_frame)
        self.recent_layout.setContentsMargins(20, 18, 20, 18)
        self.recent_layout.setSpacing(10)
        outer.addWidget(self.recent_frame)

        outer.addStretch()
        self.refresh()

    def refresh(self):
        while self.kpi_grid.count():
            item = self.kpi_grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        counts = get_counts()

        cards = [
            (
                "Medicinal Plants Catalogued",
                counts["total"],
                f"{counts['total']} in local database",
                FOREST
            ),
            (
                "Verified Plants",
                counts["verified"],
                "verified records",
                OK
            ),
            (
                "Pending Review",
                counts["pending"],
                "awaiting verification",
                SAFFRON
            ),
            (
                "Database Status",
                "Online",
                "SQLite · local",
                MOSS
            ),
        ]

        for i, (label, value, sub, accent) in enumerate(cards):
            self.kpi_grid.addWidget(
                StatCard(label, value, sub, accent),
                0, i
            )

        while self.recent_layout.count():
            item = self.recent_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        recent = get_recent_plants(5)

        if not recent:
            empty = QLabel(
                "No plants yet. Add rows to the 'plants' table "
                "to see them here."
            )
            empty.setWordWrap(True)
            empty.setStyleSheet(f"""
                color: {INK_SOFT};
                font-size: 12px;
                font-style: italic;
                border: none;
                background: transparent;
            """)
            self.recent_layout.addWidget(empty)

        else:
            for p in recent:
                row = QLabel(
                    f"•  {p.get('common_name') or p.get('sci_name')}  "
                    f"—  {p.get('sci_name', '')}   "
                    f"[{p.get('verification', '')}]"
                )
                row.setWordWrap(True)
                row.setStyleSheet(f"""
                    color: {INK};
                    font-size: 13px;
                    border: none;
                    border-bottom: 1px solid {LINE};
                    padding: 7px 2px;
                    background: transparent;
                """)
                self.recent_layout.addWidget(row)