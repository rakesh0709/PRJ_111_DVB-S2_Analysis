# PRJ_111 — DVB-S2 Receiver Output Stream Analyzer (frontend)

Plain HTML + JS, no install. `index.html` loads `js/bundle.js` (built from `js/api.js` + `js/app.js`).
If you edit the sources, rebuild the bundle: concatenate api.js (without `export`) as an IIFE, then app.js (without the import line).

## Run
1. Start the backend: `05_CODE\.venv\Scripts\python.exe 05_CODE/run_frontend.py --host 127.0.0.1 --port 8080`
2. Open `index.html` (double-click) or serve it: `python -m http.server 5173`.
The backend base URL is `http://127.0.0.1:8080`; change it in `js/api.js` or set `window.PRJ111_API` before the script loads.

## Endpoints used (verified in the backend reference)
GET /api/status · GET /api/presets · POST /api/upload (raw binary) · POST /api/analyze · POST /api/compare · GET /api/export
No demo or fixture data: every number shown comes from the backend.
