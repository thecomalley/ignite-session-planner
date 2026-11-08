# Copilot instructions

## Build, run, and validation

This is a static browser app; there is no configured build, test, or lint runner in the repository.

- Before starting a dev server, check whether port 8000 is already listening with `lsof -nP -iTCP:8000 -sTCP:LISTEN`. Reuse an existing server if available; do not start a duplicate. If the port is occupied by something else, check another port before using it. Serve the project from its root with `python3 -m http.server 8000`, then open `http://localhost:8000/ignite_planner.html` (or the selected port). The page fetches `sessions.json`, so opening it directly as a `file://` URL will not load the data.
- `python3 scrape_ignite_sessions.py` calls the live Ignite API and overwrites `sessions.json`. Only run it when the scraper code has changed and regenerating the dataset is needed; do not refresh the dataset for unrelated UI or data changes. It requires `requests` and `beautifulsoup4` in the Python environment.
- No automated test command or single-test runner is defined. For UI changes, manually verify the planner in a browser, including date navigation, search/type filters, selected-session persistence, and conflict highlighting as applicable. For scraper changes, check the normalized output against the fields consumed by the page.

## Architecture and data flow

- `ignite_planner.html` contains the entire UI: markup, styles, and client-side JavaScript. The page fetches the sibling `sessions.json`, filters and groups scheduled records, and renders a calendar by day and broad venue. Session overlap lanes and conflict highlighting are computed in the browser.
- `scrape_ignite_sessions.py` retrieves records from `https://ignite.microsoft.com/api/session/all/en-US`, normalizes API values and HTML text into the planner's record shape, sorts by start time/title, and writes `sessions.json`. Keep its output fields aligned with the fields read in the HTML, including IDs, dates/times, location, tags, metadata, session type, and session links.
- The browser uses `America/Los_Angeles` for event-day and clock display. Session timestamps retain their ISO representation; use the event timezone helpers rather than the machine's local timezone when deriving calendar dates or times.
- “My sessions” selections are stored in browser `localStorage` under `ignite-planner-selected-sessions`; selection identity combines session code/ID/title with the start and end timestamps.

## Repository-specific conventions

- Venue columns use the first portion of a location string before `|`; preserve that convention when changing location grouping.
- Dynamic session content is interpolated into HTML. Escape text and attribute values with `escapeHtml` / `escapeAttr` before inserting dataset-derived values into markup.
- The page expects scheduled records with both `start` and `end` for filtering and calendar layout. Preserve ISO-compatible timestamps so date parsing, overlap detection, and duration sizing remain consistent.
