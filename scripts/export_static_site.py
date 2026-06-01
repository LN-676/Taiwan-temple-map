import json
import shutil
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "temples.sqlite3"
STATIC_DIR = ROOT / "static"
DOCS_DIR = ROOT / "docs"
DATA_DIR = DOCS_DIR / "data"

PUBLIC_COLUMNS = [
    "id",
    "name",
    "main_deity",
    "city",
    "address",
    "religion",
    "registration_type",
    "phone",
    "longitude",
    "latitude",
    "opening_hours",
    "has_water",
    "has_meals",
    "notes",
]


def row_to_dict(row: sqlite3.Row) -> dict:
    data = {key: row[key] for key in row.keys()}
    for key in ("has_water", "has_meals"):
        if data.get(key) is not None:
            data[key] = bool(data[key])
    return data


def write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit("Database not found. Run: python3 scripts/import_temples.py")

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    shutil.copyfile(STATIC_DIR / "styles.css", DOCS_DIR / "styles.css")
    index_html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    index_html = index_html.replace('href="/styles.css"', 'href="styles.css"')
    index_html = index_html.replace('src="/app.js"', 'src="app.js"')
    (DOCS_DIR / "index.html").write_text(index_html, encoding="utf-8")

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            f"""
            SELECT {", ".join(PUBLIC_COLUMNS)}
            FROM temples
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            ORDER BY city, name
            """
        ).fetchall()
        total_count = conn.execute("SELECT COUNT(*) FROM temples").fetchone()[0]
        cities = [
            row[0]
            for row in conn.execute(
                "SELECT DISTINCT city FROM temples WHERE city <> '' ORDER BY city"
            ).fetchall()
        ]
        deities = [
            row[0]
            for row in conn.execute(
                """
                SELECT main_deity
                FROM temples
                WHERE main_deity <> ''
                GROUP BY main_deity
                ORDER BY COUNT(*) DESC, main_deity
                LIMIT 80
                """
            ).fetchall()
        ]

    temples = [row_to_dict(row) for row in rows]
    write_json(DATA_DIR / "temples.json", temples)
    write_json(
        DATA_DIR / "meta.json",
        {
            "count": total_count,
            "mapped": len(temples),
            "cities": cities,
            "deities": deities,
        },
    )

    print(f"Exported {len(temples):,} mapped temples to {DATA_DIR}")


if __name__ == "__main__":
    main()
