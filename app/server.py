import json
import sqlite3
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = ROOT / "static"
DB_PATH = ROOT / "data" / "temples.sqlite3"
HOST = "127.0.0.1"
PORT = 8000
MAX_TEMPLE_LIMIT = 20000


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

EDITABLE_COLUMNS = {"opening_hours", "has_water", "has_meals", "notes"}


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def row_to_dict(row: sqlite3.Row) -> dict:
    data = {key: row[key] for key in row.keys()}
    for key in ("has_water", "has_meals"):
        if data.get(key) is not None:
            data[key] = bool(data[key])
    return data


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def send_json(self, payload: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_error_json(self, status: HTTPStatus, message: str) -> None:
        self.send_json({"error": message}, status)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/temples":
            self.handle_temples(parsed.query)
            return
        if parsed.path.startswith("/api/temples/"):
            self.handle_temple_detail(parsed.path.rsplit("/", 1)[-1])
            return
        if parsed.path == "/api/meta":
            self.handle_meta()
            return
        if parsed.path == "/api/sources":
            self.handle_sources()
            return
        super().do_GET()

    def do_PATCH(self) -> None:
        self.send_error_json(
            HTTPStatus.FORBIDDEN,
            "Editing is disabled in the public v1 API.",
        )

    def handle_temples(self, query: str) -> None:
        params = parse_qs(query)
        limit = min(int(params.get("limit", ["600"])[0] or 600), MAX_TEMPLE_LIMIT)
        clauses = ["latitude IS NOT NULL", "longitude IS NOT NULL"]
        values: list[object] = []

        if q := params.get("q", [""])[0].strip():
            clauses.append("(name LIKE ? OR address LIKE ? OR main_deity LIKE ?)")
            values.extend([f"%{q}%", f"%{q}%", f"%{q}%"])
        if city := params.get("city", [""])[0].strip():
            clauses.append("city = ?")
            values.append(city)
        if deity := params.get("deity", [""])[0].strip():
            clauses.append("main_deity LIKE ?")
            values.append(f"%{deity}%")

        sql = f"""
            SELECT {", ".join(PUBLIC_COLUMNS)}
            FROM temples
            WHERE {" AND ".join(clauses)}
            ORDER BY city, name
            LIMIT ?
        """
        values.append(limit)

        with connect() as conn:
            rows = conn.execute(sql, values).fetchall()
        self.send_json([row_to_dict(row) for row in rows])

    def handle_temple_detail(self, temple_id: str) -> None:
        with connect() as conn:
            row = conn.execute(
                f"SELECT {', '.join(PUBLIC_COLUMNS)} FROM temples WHERE id = ?",
                (temple_id,),
            ).fetchone()
        if row is None:
            self.send_error_json(HTTPStatus.NOT_FOUND, "Temple not found")
            return
        self.send_json(row_to_dict(row))

    def handle_meta(self) -> None:
        with connect() as conn:
            count = conn.execute("SELECT COUNT(*) FROM temples").fetchone()[0]
            mapped = conn.execute(
                "SELECT COUNT(*) FROM temples WHERE latitude IS NOT NULL AND longitude IS NOT NULL"
            ).fetchone()[0]
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
        self.send_json({"count": count, "mapped": mapped, "cities": cities, "deities": deities})

    def handle_sources(self) -> None:
        with connect() as conn:
            exists = conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'data_sources'"
            ).fetchone()
            if exists is None:
                self.send_json([])
                return
            rows = conn.execute(
                """
                SELECT city, dataset_name, agency, url, format, status, note, checked_at
                FROM data_sources
                ORDER BY city, dataset_name
                """
            ).fetchall()
        self.send_json([row_to_dict(row) for row in rows])

    def handle_temple_update(self, temple_id: str) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except json.JSONDecodeError:
            self.send_error_json(HTTPStatus.BAD_REQUEST, "Invalid JSON")
            return

        updates = {key: payload[key] for key in EDITABLE_COLUMNS if key in payload}
        if not updates:
            self.send_error_json(HTTPStatus.BAD_REQUEST, "No editable fields provided")
            return

        for key in ("has_water", "has_meals"):
            if key in updates and updates[key] is not None:
                updates[key] = 1 if bool(updates[key]) else 0

        assignments = ", ".join([f"{key} = ?" for key in updates])
        values = list(updates.values()) + [temple_id]

        with connect() as conn:
            cursor = conn.execute(
                f"UPDATE temples SET {assignments}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                values,
            )
            if cursor.rowcount == 0:
                self.send_error_json(HTTPStatus.NOT_FOUND, "Temple not found")
                return
            conn.commit()
        self.handle_temple_detail(temple_id)


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit("Database not found. Run: python3 scripts/import_temples.py")
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Serving temple map at http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
