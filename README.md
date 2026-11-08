# Ignite Session Planner

A lightweight browser-based planner for Microsoft Ignite sessions. The project turns a large static dataset into a practical single-day scheduling view so it is easier to compare sessions, spot conflicts, and browse by broad venue instead of deep room names.

## What we have built so far

- One calendar view only, with prev/next day navigation
- Time-based schedule grid in Pacific Time
- Search/filter control for titles, topics, room names, and metadata
- Sessions grouped permanently into one column per broad venue (for example, Marriott Marquis instead of a full room label like Marriott Marquis | Lower B2)
- Direct time conflicts shown on the blocks themselves: a session that overlaps another gets an amber clash count
- Hovering a session highlights every session it overlaps and dims the rest, so direct conflicts are obvious
- Block height and a duration label on each session show how long it runs
- Overlapping sessions inside a venue sit side by side in lanes instead of covering each other
- On-demand and unscheduled sessions listed separately below the calendar
- Horizontal scrolling when the schedule is crowded, to preserve calendar readability without crushing the layout

## Project files

- `ignite_planner.html` – the planner UI, stylesheet, and JavaScript logic
- `sessions.json` – the current local session dataset used by the planner
- `scrape_ignite_sessions.py` – scraper that pulls Ignite session metadata from the live API and writes the JSON dataset

## How it works

The app loads `sessions.json` in the browser and builds a filtered daily schedule from the records it contains. It normalizes times into Pacific Time, groups sessions by their selected date, and renders them as event blocks over a time grid.

Each broad venue becomes a column, and sessions that overlap in time are laid out in lanes within that column. The calendar computes conflicts across all sessions on the selected day, so each block knows how many other sessions it overlaps with. Hovering a block highlights those overlaps and dims everything else. The venue grouping logic uses the first section of a location string before a pipe, which keeps high-level planning readable without getting lost in exact-room granularity.

## Running it locally

From the project folder:

```bash
cd /Users/chris/code/Ignite
python3 -m http.server 8000
```

Then open:

```text
http://localhost:8000/ignite_planner.html
```

The page expects to be served over a local HTTP server so it can fetch `sessions.json` correctly.

## Current design intent

This planner is intentionally optimized for a calendar-first workflow, not a generic agenda dump. The main goal is to support quick triage of a crowded day:

- keep the calendar as the only view
- make direct time conflicts visible without a separate comparison step
- show session length directly on the block
- group by broad venue to reduce visual noise
- retain horizontal overflow only where the schedule is genuinely dense

## Current status

The project is in a working, exploratory state and already captures the core planner workflow we wanted:

- one-day planning
- realistic dense-event layout
- venue-level grouping
- direct conflict detection and hover highlighting
- filterable schedule view

It is still being refined as a practical planning tool, especially around the final visual balance between density, readability, and the feel of a drawn-out schedule sketch.

## Notes

The current dataset is generated from the Ignite live session API and stored locally. If the event list changes upstream, re-run the scraper to refresh the JSON feed:

```bash
python3 scrape_ignite_sessions.py
```
