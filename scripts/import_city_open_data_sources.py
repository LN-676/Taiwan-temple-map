import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "temples.sqlite3"


SCHEMA = """
CREATE TABLE IF NOT EXISTS data_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    dataset_name TEXT NOT NULL,
    agency TEXT,
    url TEXT NOT NULL,
    format TEXT,
    status TEXT NOT NULL,
    note TEXT DEFAULT '',
    checked_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(city, dataset_name, url)
);
"""


SOURCES = [
    {
        "city": "臺北市",
        "dataset_name": "臺北市寺廟一覽",
        "agency": "臺北市政府民政局",
        "url": "https://data.taipei/dataset/detail?id=b5f043ce-00be-4404-b975-02e29fe10f51",
        "format": "ODS",
        "note": "欄位含編號、寺廟名稱、聯絡電話、縣市、行政區、所在地。",
    },
    {
        "city": "臺北市",
        "dataset_name": "臺北市已立案宗教團體點位資料",
        "agency": "臺北市政府民政局",
        "url": "https://data.gov.tw/dataset/121141",
        "format": "ODS",
        "note": "欄位含寺廟名稱、行政區、里、教別、祭典日期、電話、地址、X/Y座標。",
    },
    {
        "city": "新北市",
        "dataset_name": "新北市寺廟資料",
        "agency": "新北市政府民政局",
        "url": "https://data.gov.tw/dataset/122928",
        "format": "CSV",
        "note": "欄位含寺廟名稱、地址、電話、主祀神祇、節慶活動日期、WGS84座標。",
    },
    {
        "city": "桃園市",
        "dataset_name": "桃園市寺廟名冊",
        "agency": "桃園市政府",
        "url": "https://opendata.tycg.gov.tw/datalist/6484b20f-8525-4437-ae81-d1e1601067d0",
        "format": "CSV/API",
        "note": "桃園資料開放平台資料集。",
    },
    {
        "city": "臺中市",
        "dataset_name": "臺中市宗教名冊",
        "agency": "臺中市政府",
        "url": "https://opendata.taichung.gov.tw/search/3410148c-89ff-4026-9737-8634930ca869",
        "format": "CSV/API",
        "note": "臺中市宗教含寺廟、教會名冊。",
    },
    {
        "city": "高雄市",
        "dataset_name": "寺廟名冊",
        "agency": "高雄市三民區公所",
        "url": "https://data.gov.tw/dataset/166357",
        "format": "CSV/JSON",
        "note": "三民區資料，欄位含寺廟名稱、主祀神祇、電話、里別、地址、宗教別、負責人。",
    },
    {
        "city": "新竹市",
        "dataset_name": "新竹市寺廟名冊",
        "agency": "新竹市政府民政處",
        "url": "https://data.gov.tw/dataset/67532",
        "format": "CSV/XML/JSON/XLSX",
        "note": "欄位含寺廟名稱、主祀神像、教別、建別、組織型態、所在地、電話。",
    },
    {
        "city": "新竹縣",
        "dataset_name": "新竹縣已登記寺廟一覽表",
        "agency": "新竹縣政府民政處",
        "url": "https://data.gov.tw/dataset/109237",
        "format": "CSV/XML/JSON/XLSX",
        "note": "欄位含鄉別、寺廟名稱、主祀神佛像、教別、地址、負責人、電話。",
    },
    {
        "city": "宜蘭縣",
        "dataset_name": "宜蘭縣寺廟名冊一覽表",
        "agency": "宜蘭縣政府",
        "url": "https://civil.e-land.gov.tw/cp.aspx?n=9725",
        "format": "網頁/檔案",
        "note": "宜蘭縣宗教團體資料頁。",
    },
    {
        "city": "苗栗縣",
        "dataset_name": "苗栗縣寺廟登記表檢索",
        "agency": "苗栗縣政府",
        "url": "https://webws.miaoli.gov.tw/Download.ashx?n=MjAxMDA2MDgwNTI3NTExMTQ4MzQ1NjE1LnBkZg%3D%3D&u=LzAwMS9VcGxvYWQvNDYwL3JlbGZpbGUvOTMwMS85NjIvNzVjNTRhZTAtNjliMy00N2NiLWJiMzUtMDFlODIzZTJlMWE5LnBkZg%3D%3D",
        "format": "PDF",
        "note": "欄位含寺廟名稱、住址、祭典日期、電話、主祀神佛像。",
    },
    {
        "city": "嘉義縣",
        "dataset_name": "嘉義縣已登記寺廟一覽表",
        "agency": "嘉義縣政府",
        "url": "https://data.gov.tw/dataset/21825",
        "format": "PDF",
        "note": "政府資料開放平台資料集。",
    },
    {
        "city": "嘉義市",
        "dataset_name": "嘉義市寺廟名冊",
        "agency": "嘉義市政府",
        "url": "https://icmp-ws.chiayi.gov.tw/Download.ashx?n=5ZiJ576p5biC5a%2B65buf5ZCN5YaKKOe2suermSkucGRm&u=LzAwMS9VcGxvYWQvNDA3L3JlbGZpbGUvOTEzNC83NzAvNDVlZWJjYTktOTUwOS00M2MwLTkzMDktNzVlMGIyM2YzN2JlLnBkZg%3D%3D",
        "format": "PDF",
        "note": "欄位含單位名稱、地址、電話。",
    },
    {
        "city": "雲林縣",
        "dataset_name": "雲林縣政府登記有案寺廟名冊",
        "agency": "雲林縣政府",
        "url": "https://civil.yunlin.gov.tw/News_Content.aspx?n=1558&s=254390",
        "format": "網頁/PDF",
        "note": "雲林縣政府民政處資料頁。",
    },
    {
        "city": "金門縣",
        "dataset_name": "金城鎮寺廟一覽表",
        "agency": "金門縣金城鎮公所",
        "url": "https://jincheng.kinmen.gov.tw/cp.aspx?n=FB52FF37B28E1B43",
        "format": "網頁",
        "note": "欄位含寺廟名稱、主祀神佛像、寺廟地址。",
    },
]


def existing_cities(conn: sqlite3.Connection) -> set[str]:
    return {row[0] for row in conn.execute("SELECT DISTINCT city FROM temples WHERE city <> ''")}


def main() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA)
        cities = existing_cities(conn)
        rows = []
        for source in SOURCES:
            status = "skipped_existing_city" if source["city"] in cities else "ready_to_import"
            rows.append(
                (
                    source["city"],
                    source["dataset_name"],
                    source["agency"],
                    source["url"],
                    source["format"],
                    status,
                    source["note"],
                )
            )
        conn.executemany(
            """
            INSERT INTO data_sources (city, dataset_name, agency, url, format, status, note)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(city, dataset_name, url) DO UPDATE SET
                agency=excluded.agency,
                format=excluded.format,
                status=excluded.status,
                note=excluded.note,
                checked_at=CURRENT_TIMESTAMP
            """,
            rows,
        )
        skipped = sum(1 for row in rows if row[5] == "skipped_existing_city")
        ready = len(rows) - skipped
    print(f"Saved {len(rows)} city data sources. skipped={skipped}, ready_to_import={ready}")


if __name__ == "__main__":
    main()
