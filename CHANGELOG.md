# Changelog

## v1 - Static public release

- Added a GitHub Pages-ready static site under `docs/`.
- Exported mapped temple records from SQLite to `docs/data/temples.json`.
- Exported summary metadata to `docs/data/meta.json`.
- Updated the public frontend to read local JSON instead of `/api/*`.
- Disabled `PATCH /api/temples/{id}` in the local backend. It now returns
  `403 Forbidden`, so the public v1 does not expose a write API.
- Kept the Python backend for local development and future API work.
