#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = ROOT / "sessions.json"
SESSION_API_URL = "https://ignite.microsoft.com/api/session/all/en-US"


def clean_html_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        text = value
    else:
        text = str(value)
    text = BeautifulSoup(text, "html.parser").get_text(" ", strip=True)
    return re.sub(r"\s+", " ", text).strip()


def get_display_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        for key in ("displayValue", "logicalValue", "value"):
            text = value.get(key)
            if text:
                return str(text).strip()
        return " ".join(str(v).strip() for v in value.values() if str(v).strip())
    if isinstance(value, list):
        values = [get_display_value(item) for item in value]
        return ", ".join(v for v in values if v)
    return str(value).strip()


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        try:
            return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            return None


def format_12_hour(value: datetime | None) -> str:
    if value is None:
        return ""
    return value.strftime("%I:%M %p").replace(" 0", " ").strip()


def normalize_session(raw: dict[str, Any]) -> dict[str, Any] | None:
    title = clean_html_text(raw.get("title") or "").strip()
    if not title:
        return None

    start_dt = parse_datetime(raw.get("startDateTime"))
    end_dt = parse_datetime(raw.get("endDateTime"))

    location = get_display_value(raw.get("location"))
    tags = []
    for entry in raw.get("tags") or []:
        value = get_display_value(entry)
        if value and value not in tags:
            tags.append(value)

    session_type = get_display_value(raw.get("sessionType"))
    speaker_names = clean_html_text(raw.get("speakerNames") or "")
    description = clean_html_text(raw.get("description") or raw.get("aiDescription") or "")
    content_areas = [get_display_value(item) for item in raw.get("contentArea") or []]
    metadata = [piece for piece in [session_type, location, speaker_names, *content_areas] if piece]

    session_code = raw.get("sessionCode")
    session_id = raw.get("sessionId") or session_code or raw.get("localizedId") or raw.get("title")
    session_url = (
        f"https://ignite.microsoft.com/en-US/sessions/{session_code}"
        if session_code
        else "https://ignite.microsoft.com/en-US/sessions"
    )

    record = {
        "id": session_id,
        "title": title,
        "url": session_url,
        "date": start_dt.strftime("%Y-%m-%d") if start_dt else "",
        "time_text": f"{format_12_hour(start_dt)} - {format_12_hour(end_dt)}" if start_dt and end_dt else "",
        "start": start_dt.isoformat() if start_dt else None,
        "end": end_dt.isoformat() if end_dt else None,
        "location": location,
        "eyebrow": session_type,
        "tags": tags,
        "metadata": metadata,
        "abstract": description,
        "speakerNames": speaker_names,
        "sessionCode": session_code,
        "sessionType": session_type,
        "source_file": "live-api",
    }

    if not record["id"]:
        record["id"] = re.sub(r"\s+", " ", title).lower()
    return record


def fetch_live_sessions() -> list[dict[str, Any]]:
    response = requests.get(SESSION_API_URL, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list):
        raise ValueError(f"Unexpected session API payload type: {type(payload).__name__}")

    sessions = []
    for raw in payload:
        session = normalize_session(raw)
        if session:
            sessions.append(session)

    return sorted(sessions, key=lambda item: (item.get("start") or "", item.get("title") or ""))


def main() -> None:
    sessions = fetch_live_sessions()
    OUTPUT_PATH.write_text(json.dumps(sessions, indent=2), encoding="utf-8")
    print(f"Written {len(sessions)} sessions to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
