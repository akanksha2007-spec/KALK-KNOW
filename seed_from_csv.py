"""
Kalki Know — seed SQLite from CSVs.
Run once:  python seed_from_csv.py
Safe to re-run: skips existing rows.
"""

import os
import csv
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "kalki.db")
PLANTS_CSV = os.path.join(BASE_DIR, "kalki_know_plant_info.csv")
REMEDIES_CSV = os.path.join(BASE_DIR, "Remedies_Cleaned_Dataset.csv")


def ensure_schema(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS plants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sci_name TEXT UNIQUE,
            common_name TEXT,
            family TEXT,
            regional_name TEXT,
            sanskrit_name TEXT,
            category TEXT,
            conservation TEXT,
            verification TEXT DEFAULT 'Pending Review',
            ai_confidence REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("PRAGMA table_info(plants)")
    existing = {row[1] for row in cur.fetchall()}
    extras = {
        "traditional_uses": "TEXT",
        "key_compounds": "TEXT",
        "safety_notes": "TEXT",
        "plant_part_used": "TEXT",
        "native_region": "TEXT",
        "habitat": "TEXT",
        "source_url": "TEXT",
        "image_path": "TEXT",
    }
    for col, typ in extras.items():
        if col not in existing:
            cur.execute(f"ALTER TABLE plants ADD COLUMN {col} {typ}")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS remedies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disease TEXT,
            plant_common_name TEXT,
            sci_name TEXT,
            plant_part TEXT,
            phytochemical TEXT,
            therapeutic_use TEXT,
            preparation TEXT,
            dosage_form TEXT,
            usage_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()


def seed_plants(conn):
    cur = conn.cursor()
    added, skipped = 0, 0
    with open(PLANTS_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sci = (row.get("scientific_name") or "").strip()
            if not sci:
                continue
            cur.execute("SELECT id FROM plants WHERE sci_name = ?", (sci,))
            if cur.fetchone():
                skipped += 1
                continue
            cur.execute("""
                INSERT INTO plants (
                    sci_name, common_name, family, regional_name, sanskrit_name,
                    category, conservation, verification,
                    traditional_uses, key_compounds, safety_notes,
                    plant_part_used, native_region, habitat, source_url
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                sci,
                row.get("common_name", "").strip(),
                row.get("family", "").strip(),
                row.get("regional_names", "").strip(),
                row.get("sanskrit_name", "").strip(),
                row.get("plant_part_used", "").strip(),
                row.get("conservation_status", "").strip(),
                row.get("verification_status", "").strip() or "Pending Review",
                row.get("traditional_uses", "").strip(),
                row.get("key_compounds", "").strip(),
                row.get("safety_notes", "").strip(),
                row.get("plant_part_used", "").strip(),
                row.get("native_region", "").strip(),
                row.get("habitat", "").strip(),
                row.get("source_url", "").strip(),
            ))
            added += 1
    conn.commit()
    return added, skipped


def seed_remedies(conn):
    cur = conn.cursor()
    added = 0
    with open(REMEDIES_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sci = (row.get("Scientific_Name") or "").strip()
            disease = (row.get("Disease") or "").strip()
            cur.execute("SELECT id FROM remedies WHERE sci_name = ? AND disease = ?",
                        (sci, disease))
            if cur.fetchone():
                continue
            cur.execute("""
                INSERT INTO remedies (
                    disease, plant_common_name, sci_name, plant_part,
                    phytochemical, therapeutic_use, preparation,
                    dosage_form, usage_notes
                ) VALUES (?,?,?,?,?,?,?,?,?)
            """, (
                disease,
                row.get("Plant_Name", "").strip(),
                sci,
                row.get("Plant_Part", "").strip(),
                row.get("Phytochemical", "").strip(),
                row.get("Therapeutic_Use", "").strip(),
                row.get("Remedy_Preparation", "").strip(),
                row.get("Dosage_Form", "").strip(),
                row.get("Usage_Notes", "").strip(),
            ))
            added += 1
    conn.commit()
    return added


def auto_add_orphan_plants(conn):
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT sci_name, plant_common_name, plant_part FROM remedies")
    orphans = 0
    for sci, common, part in cur.fetchall():
        if not sci:
            continue
        cur.execute("SELECT id FROM plants WHERE sci_name = ?", (sci,))
        if cur.fetchone():
            continue
        cur.execute("""
            INSERT INTO plants (sci_name, common_name, plant_part_used, verification)
            VALUES (?, ?, ?, 'Pending Review')
        """, (sci, common, part))
        orphans += 1
    conn.commit()
    return orphans


if __name__ == "__main__":
    if not os.path.exists(PLANTS_CSV):
        print(f"Missing: {PLANTS_CSV}")
        raise SystemExit(1)
    if not os.path.exists(REMEDIES_CSV):
        print(f"Missing: {REMEDIES_CSV}")
        raise SystemExit(1)

    conn = sqlite3.connect(DB_PATH)
    ensure_schema(conn)

    p_added, p_skipped = seed_plants(conn)
    r_added = seed_remedies(conn)
    orphans = auto_add_orphan_plants(conn)

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM plants")
    total_plants = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM remedies")
    total_remedies = cur.fetchone()[0]

    print(f"Plants added:    {p_added}  (skipped {p_skipped} existing)")
    print(f"Remedies added:  {r_added}")
    print(f"Orphan plants added from remedies: {orphans}")
    print("---")
    print(f"Total plants in DB:   {total_plants}")
    print(f"Total remedies in DB: {total_remedies}")
    conn.close()