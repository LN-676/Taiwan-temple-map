# Taiwan Temple Map v1

Python backend + OpenStreetMap frontend for Taiwan registered temple data.

The v1 public release is a read-only static website under `docs/` for GitHub
Pages. It does not expose a public write API.

## Data Source

- Government dataset: 全國宗教資訊系統資料-寺廟
- URL: https://data.gov.tw/dataset/8203
- XML download: https://religion.moi.gov.tw/Report/temple.xml

The official XML currently includes temple name, deity, city/admin area, address,
religion, registration type, phone, owner, notes, and WGS84 coordinates.
Opening hours, water, and meals are MVP-editable local fields.

## Run

### Static GitHub Pages version

Public site:

https://ln-676.github.io/Taiwan-temple-map/

```bash
python3 scripts/fetch_temples.py
python3 scripts/import_temples.py
python3 scripts/import_city_open_data_sources.py
python3 scripts/export_static_site.py
```

Publish `main` / `docs` with GitHub Pages.

### Local backend version

```bash
python3 scripts/fetch_temples.py
python3 scripts/import_temples.py
python3 scripts/import_city_open_data_sources.py
python3 app/server.py
```

Local development URL:

http://127.0.0.1:8000

## API

- `GET /api/temples?q=&city=&deity=&limit=500`
- `GET /api/temples/{id}`
- `GET /api/meta`
- `GET /api/sources`

Editing is disabled in v1. `PATCH /api/temples/{id}` returns `403 Forbidden`.

`/api/sources` records county/city open-data sources found during research. The
current national dataset already covers all 22 cities/counties, so these local
sources are marked `skipped_existing_city` unless the main data is missing that
city in the future.

The static site reads `docs/data/meta.json` and `docs/data/temples.json`
directly in the browser, so GitHub Pages can host it without Python or SQLite.
