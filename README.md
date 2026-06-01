# Taiwan Temple Map MVP

Python backend + OpenStreetMap frontend for Taiwan registered temple data.

## Data Source

- Government dataset: 全國宗教資訊系統資料-寺廟
- URL: https://data.gov.tw/dataset/8203
- XML download: https://religion.moi.gov.tw/Report/temple.xml

The official XML currently includes temple name, deity, city/admin area, address,
religion, registration type, phone, owner, notes, and WGS84 coordinates.
Opening hours, water, and meals are MVP-editable local fields.

## Run

```bash
python3 scripts/fetch_temples.py
python3 scripts/import_temples.py
python3 scripts/import_city_open_data_sources.py
python3 app/server.py
```

Open http://127.0.0.1:8000

## API

- `GET /api/temples?q=&city=&deity=&limit=500`
- `GET /api/temples/{id}`
- `PATCH /api/temples/{id}`
- `GET /api/meta`
- `GET /api/sources`

`/api/sources` records county/city open-data sources found during research. The
current national dataset already covers all 22 cities/counties, so these local
sources are marked `skipped_existing_city` unless the main data is missing that
city in the future.

Example update:

```bash
curl -X PATCH http://127.0.0.1:8000/api/temples/1746804 \
  -H 'Content-Type: application/json' \
  -d '{"opening_hours":"06:00-21:00","has_water":true,"has_meals":false,"notes":"初一十五人潮較多"}'
```
