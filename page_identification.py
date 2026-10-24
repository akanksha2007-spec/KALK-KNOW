"""
Kalki Know — Plant Identification page.
Uses the trained ResNet50 model for real inference.
"""

import os
import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame,
    QPushButton, QFileDialog, QScrollArea
)

import torch
import torch.nn.functional as F
from torchvision import transforms, models
from PIL import Image

FOREST      = "#244D39"
FOREST_DEEP = "#203128"
PARCHMENT   = "#F5F2E9"
CARD        = "#FFFEFA"
SAFFRON     = "#C5A15A"
TERRACOTTA  = "#B9654D"
INK         = "#203128"
INK_SOFT    = "#68776B"
LINE        = "#E4DFD2"
OK          = "#427653"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "kalki.db")
MODEL_PATH = os.path.join(BASE_DIR, "kalki_plant_model.pth")
CLASSES_PATH = os.path.join(BASE_DIR, "classes.txt")
PLANTS_TABLE = "plants"


# ------------------------------------------------------------------
# Class name mapping — 15 classes
# ------------------------------------------------------------------
CLASS_TO_SCI = {
    "Ocimum_tenuiflorum": "Ocimum tenuiflorum",
    "Azadirachta_indica": "Azadirachta indica",
    "Aloe_vera": "Aloe vera",
    "Curcuma_longa": "Curcuma longa",
    "Withania_somnifera": "Withania somnifera",
    "Phyllanthus_emblica": "Phyllanthus emblica",
    "Bacopa_monnieri": "Bacopa monnieri",
    "Zingiber_officinale": "Zingiber officinale",
    "Tinospora_cordifolia": "Tinospora cordifolia",
    "Piper_nigrum": "Piper nigrum",
    "Elettaria_cardamomum": "Elettaria cardamomum",
    "Mentha_spicata": "Mentha spicata",
    "Coriandrum_sativum": "Coriandrum sativum",
    "Trigonella_foenum-graecum": "Trigonella foenum-graecum",
    "Moringa_oleifera": "Moringa oleifera",
}


# ------------------------------------------------------------------
# Model loading + prediction (ResNet50)
# ------------------------------------------------------------------
_model = None
_classes = None

_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225]
    ),
])


def _load_model():
    global _model, _classes

    if _model is not None:
        return _model, _classes

    if not os.path.exists(MODEL_PATH) or not os.path.exists(CLASSES_PATH):
        return None, None

    with open(CLASSES_PATH, "r", encoding="utf-8") as f:
        _classes = [line.strip() for line in f if line.strip()]

    _model = models.resnet50(weights=None)
    _model.fc = torch.nn.Linear(
        _model.fc.in_features,
        len(_classes)
    )
    _model.load_state_dict(
        torch.load(MODEL_PATH, map_location="cpu")
    )
    _model.eval()

    return _model, _classes


def predict_plant(image_path):
    """Real inference using the trained model."""
    model, classes = _load_model()

    if model is None:
        return None

    try:
        img = Image.open(image_path).convert("RGB")
        tensor = _transform(img).unsqueeze(0)

        with torch.no_grad():
            logits = model(tensor)
            probs = F.softmax(logits, dim=1)
            conf, idx = probs.max(1)

        raw_class = classes[idx.item()]
        sci_name = CLASS_TO_SCI.get(raw_class, raw_class)

        return {
            "sci_name": sci_name,
            "confidence": float(conf.item()),
            "raw_class": raw_class,
        }

    except Exception:
        return None


# ------------------------------------------------------------------
# Database helpers
# ------------------------------------------------------------------
def get_counts():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {PLANTS_TABLE}")
    total = cur.fetchone()[0]
    conn.close()
    return {"total": total}


def get_plant_by_sci_name(sci_name):
    """Look up a plant by sci_name; if not found, try a LIKE match."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(
        f"SELECT * FROM {PLANTS_TABLE} WHERE sci_name = ? LIMIT 1",
        (sci_name,)
    )
    row = cur.fetchone()

    if not row:
        cur.execute(
            f"SELECT * FROM {PLANTS_TABLE} WHERE sci_name LIKE ? LIMIT 1",
            (f"%{sci_name}%",)
        )
        row = cur.fetchone()

    conn.close()
    return dict(row) if row else None


# ------------------------------------------------------------------
# The page
# ------------------------------------------------------------------
class Page(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet(f"background:{PARCHMENT};")
        self.image_path = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(30, 26, 30, 30)
        outer.setSpacing(17)

        # Title
        title = QLabel("Plant Identification")
        title.setStyleSheet(f"""
            color: {FOREST_DEEP};
            font-size: 25px;
            font-weight: 700;
            background: transparent;
        """)
        outer.addWidget(title)

        sub = QLabel(
            "Upload a plant photo to identify its species "
            "and view the available plant information."
        )
        sub.setWordWrap(True)
        sub.setStyleSheet(f"""
            color: {INK_SOFT};
            font-size: 13px;
            background: transparent;
        """)
        outer.addWidget(sub)

        split = QHBoxLayout()
        split.setSpacing(18)

        # ---- LEFT: image + buttons ----
        left = QFrame()
        left.setObjectName("UploadCard")
        left.setMinimumWidth(360)
        left.setStyleSheet(f"""
            QFrame#UploadCard {{
                background: {CARD};
                border: 1px solid {LINE};
                border-radius: 15px;
            }}
        """)

        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(18, 18, 18, 18)
        left_layout.setSpacing(14)

        self.image_label = QLabel("No image uploaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(300, 330)
        self.image_label.setStyleSheet(f"""
            background: #F0F2E9;
            color: {INK_SOFT};
            border: 1px dashed #C8D2C1;
            border-radius: 12px;
            font-size: 13px;
        """)
        left_layout.addWidget(self.image_label, 1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        upload_btn = QPushButton("Upload Image")
        upload_btn.setCursor(Qt.PointingHandCursor)
        upload_btn.setMinimumHeight(42)
        upload_btn.setStyleSheet(f"""
            QPushButton {{
                background: {FOREST};
                color: white;
                border: none;
                border-radius: 9px;
                padding: 10px 15px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: #193A2D;
            }}
        """)
        upload_btn.clicked.connect(self.upload_image)
        btn_row.addWidget(upload_btn)

        self.identify_btn = QPushButton("Identify Plant")
        self.identify_btn.setCursor(Qt.PointingHandCursor)
        self.identify_btn.setMinimumHeight(42)
        self.identify_btn.setStyleSheet(f"""
            QPushButton {{
                background: {SAFFRON};
                color: #203128;
                border: none;
                border-radius: 9px;
                padding: 10px 15px;
                font-size: 13px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background: #B48C45;
            }}
            QPushButton:disabled {{
                background: #E5E1D7;
                color: #899187;
            }}
        """)
        self.identify_btn.clicked.connect(self.identify)
        self.identify_btn.setEnabled(False)
        btn_row.addWidget(self.identify_btn)

        left_layout.addLayout(btn_row)
        split.addWidget(left, 1)

        # ---- RIGHT: results ----
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)

        right = QWidget()
        right.setStyleSheet("background: transparent;")

        self.results_layout = QVBoxLayout(right)
        self.results_layout.setContentsMargins(0, 0, 4, 0)
        self.results_layout.setSpacing(14)
        self.results_layout.addStretch()

        right_scroll.setWidget(right)
        split.addWidget(right_scroll, 1)

        outer.addLayout(split, 1)

    # --------------------------------------------------------------
    def upload_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select plant image",
            "",
            "Images (*.jpg *.jpeg *.png *.bmp)"
        )

        if not path:
            return

        self.image_path = path
        pix = QPixmap(path)

        if pix.isNull():
            self.image_label.setText("Could not load image")
            return

        self.image_label.setPixmap(
            pix.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

        self.image_label.setStyleSheet(f"""
            background: #F0F2E9;
            border: 1px solid {LINE};
            border-radius: 12px;
        """)
        self.identify_btn.setEnabled(True)

    # --------------------------------------------------------------
    def _clear_results(self):
        while self.results_layout.count() > 1:
            item = self.results_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    # --------------------------------------------------------------
    def identify(self):
        if not self.image_path:
            return

        self._clear_results()

        if not os.path.exists(MODEL_PATH):
            msg = QLabel(
                "Model not found. Please train the model first."
            )
            msg.setStyleSheet(
                f"color:{TERRACOTTA}; font-size:13px;"
            )
            msg.setWordWrap(True)
            self.results_layout.insertWidget(0, msg)
            return

        # Run prediction
        prediction = predict_plant(self.image_path)

        if not prediction:
            msg = QLabel(
                "Identification failed. Could not process the image."
            )
            msg.setStyleSheet(
                f"color:{TERRACOTTA}; font-size:13px;"
            )
            msg.setWordWrap(True)
            self.results_layout.insertWidget(0, msg)
            return

        conf_pct = int(prediction["confidence"] * 100)

        # ---- CONFIDENCE THRESHOLD (40%) ----
        if prediction["confidence"] < 0.40:
            warn = QLabel(
                f"Could not confidently identify this plant "
                f"(Confidence: {conf_pct}%).\n\n"
                "Try uploading a clearer, closer photo of a "
                "single leaf on a plain background."
            )
            warn.setStyleSheet("""
                color: #7C3027;
                font-size: 13px;
                background: #F8E9E3;
                border: 1px solid #EBD0C6;
                border-radius: 10px;
                padding: 14px;
            """)
            warn.setWordWrap(True)
            self.results_layout.insertWidget(0, warn)
            return

        conf_color = (
            OK if conf_pct >= 90
            else (SAFFRON if conf_pct >= 75 else TERRACOTTA)
        )

        plant = get_plant_by_sci_name(prediction["sci_name"])

        # ---- Result card ----
        result_card = QFrame()
        result_card.setObjectName("ResultCard")
        result_card.setStyleSheet(f"""
            QFrame#ResultCard {{
                background: {CARD};
                border: 1px solid {LINE};
                border-radius: 15px;
            }}
        """)

        rc = QVBoxLayout(result_card)
        rc.setContentsMargins(20, 20, 20, 20)
        rc.setSpacing(9)

        lbl = QLabel("IDENTIFIED SPECIES")
        lbl.setStyleSheet(f"""
            color: {INK_SOFT};
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
            background: transparent;
            border: none;
        """)
        rc.addWidget(lbl)

        display_name = (
            plant.get("common_name")
            if plant else prediction["raw_class"].replace("_", " ")
        ) or prediction["raw_class"]

        name = QLabel(display_name)
        name.setStyleSheet(f"""
            color: {FOREST_DEEP};
            font-size: 23px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        name.setWordWrap(True)
        rc.addWidget(name)

        sci = QLabel(prediction["sci_name"])
        sci.setStyleSheet(f"""
            color: {INK_SOFT};
            font-size: 13px;
            font-style: italic;
            background: transparent;
            border: none;
        """)
        rc.addWidget(sci)

        conf = QLabel(f"Confidence: {conf_pct}%")
        conf.setStyleSheet(f"""
            color: {conf_color};
            font-size: 13px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        rc.addWidget(conf)

        self.results_layout.insertWidget(0, result_card)

        # ---- If plant is not in DB ----
        if not plant:
            warn = QLabel(
                f"Detected as \"{prediction['raw_class'].replace('_', ' ')}\", "
                "but this species isn't in the local database yet, "
                "so full plant information isn't available."
            )
            warn.setStyleSheet("""
                color: #7C3027;
                font-size: 12.5px;
                background: #F8E9E3;
                border: 1px solid #EBD0C6;
                border-radius: 10px;
                padding: 13px;
            """)
            warn.setWordWrap(True)
            self.results_layout.insertWidget(1, warn)
            return

        # ---- Info card ----
        info_card = QFrame()
        info_card.setObjectName("PlantInfoCard")
        info_card.setStyleSheet(f"""
            QFrame#PlantInfoCard {{
                background: {CARD};
                border: 1px solid {LINE};
                border-radius: 15px;
            }}
        """)

        ic = QVBoxLayout(info_card)
        ic.setContentsMargins(20, 20, 20, 20)
        ic.setSpacing(12)

        info_title = QLabel("Plant Information")
        info_title.setStyleSheet(f"""
            color: {FOREST_DEEP};
            font-size: 16px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        ic.addWidget(info_title)

        fields = [
            ("Scientific Name", plant.get("sci_name")),
            ("Common Name", plant.get("common_name")),
            ("Family", plant.get("family")),
            ("Regional Name", plant.get("regional_name")),
            ("Sanskrit Name", plant.get("sanskrit_name")),
            ("Plant Part Used", plant.get("plant_part_used")),
            ("Medicinal Category", plant.get("category")),
            ("Conservation Status", plant.get("conservation")),
            ("Habitat", plant.get("habitat")),
            ("Traditional Uses", plant.get("traditional_uses")),
            ("Key Compounds", plant.get("key_compounds")),
            ("Safety Notes", plant.get("safety_notes")),
            ("Verification", plant.get("verification")),
        ]

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(11)

        row = 0

        for k, v in fields:
            if not v:
                continue

            k_lbl = QLabel(k)
            k_lbl.setStyleSheet(f"""
                color: {INK_SOFT};
                font-size: 11.5px;
                font-weight: 600;
                background: transparent;
                border: none;
            """)

            v_lbl = QLabel(str(v))
            v_lbl.setStyleSheet(f"""
                color: {INK};
                font-size: 13px;
                background: transparent;
                border: none;
            """)
            v_lbl.setWordWrap(True)

            grid.addWidget(k_lbl, row, 0, Qt.AlignTop)
            grid.addWidget(v_lbl, row, 1)
            row += 1

        ic.addLayout(grid)
        self.results_layout.insertWidget(1, info_card)