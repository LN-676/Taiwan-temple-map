import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
XML_PATHS = [ROOT / "data" / "temple.xml", ROOT / "temple.xml"]
DB_PATH = ROOT / "data" / "temples.sqlite3"


SCHEMA = """
CREATE TABLE IF NOT EXISTS temples (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    main_deity TEXT,
    city TEXT,
    address TEXT,
    religion TEXT,
    registration_type TEXT,
    tax_id TEXT,
    phone TEXT,
    owner TEXT,
    source_notes TEXT,
    longitude REAL,
    latitude REAL,
    opening_hours TEXT DEFAULT '尚未提供',
    has_water INTEGER DEFAULT NULL,
    has_meals INTEGER DEFAULT NULL,
    notes TEXT DEFAULT '',
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_temples_city ON temples(city);
CREATE INDEX IF NOT EXISTS idx_temples_deity ON temples(main_deity);
CREATE INDEX IF NOT EXISTS idx_temples_name ON temples(name);
"""


def text(node: ET.Element, tag: str) -> str:
    child = node.find(tag)
    return (child.text or "").strip() if child is not None else ""


def number(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def find_xml_path() -> Path:
    for path in XML_PATHS:
        if path.exists():
            return path
    raise FileNotFoundError("No temple XML found. Run scripts/fetch_temples.py first.")


def main() -> None:
    xml_path = find_xml_path()
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    tree = ET.parse(xml_path)
    root = tree.getroot()

    rows = []
    for item in root.findall(".//OpenData_3"):
        temple_id = text(item, "編號") or f"{text(item, '寺廟名稱')}|{text(item, '地址')}"
        rows.append(
            (
                temple_id,
                text(item, "寺廟名稱"),
                text(item, "主祀神祇"),
                text(item, "行政區"),
                text(item, "地址"),
                text(item, "教別"),
                text(item, "登記別"),
                text(item, "統一編號"),
                text(item, "電話"),
                text(item, "負責人"),
                text(item, "其他"),
                number(text(item, "WGS84X")),
                number(text(item, "WGS84Y")),
            )
        )

    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA)
        conn.executemany(
            """
            INSERT INTO temples (
                id, name, main_deity, city, address, religion, registration_type,
                tax_id, phone, owner, source_notes, longitude, latitude
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name,
                main_deity=excluded.main_deity,
                city=excluded.city,
                address=excluded.address,
                religion=excluded.religion,
                registration_type=excluded.registration_type,
                tax_id=excluded.tax_id,
                phone=excluded.phone,
                owner=excluded.owner,
                source_notes=excluded.source_notes,
                longitude=excluded.longitude,
                latitude=excluded.latitude
            """,
            rows,
        )

    print(f"Imported {len(rows):,} temples into {DB_PATH}")


if __name__ == "__main__":
    main()
