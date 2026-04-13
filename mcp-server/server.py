from __future__ import annotations

import os
import time

import httpx
from fastmcp import FastMCP

SCHEDULE_URL = "https://ec26.qaware.de/ec26/schedule/export/schedule.json"
CACHE_TTL_SECONDS = int(os.environ.get("CACHE_TTL_SECONDS", "900"))
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))


class ScheduleCache:
    def __init__(self, cache_ttl_seconds: int = CACHE_TTL_SECONDS):
        self._cache_ttl_seconds = cache_ttl_seconds
        self._raw_data: dict | None = None
        self._last_fetch: float = 0.0
        self.conference: dict = {}
        self.talks_by_day: dict[str, list[dict]] = {}
        self.talks_by_track: dict[str, list[dict]] = {}
        self.talks_by_code: dict[str, dict] = {}
        self.speakers: dict[str, dict] = {}
        self._day_index_map: dict[str, str] = {}

    @property
    def is_stale(self) -> bool:
        if self._raw_data is None:
            return True
        return (time.time() - self._last_fetch) > self._cache_ttl_seconds

    def day_index_to_date(self, day: str) -> str | None:
        if day in self._day_index_map:
            return self._day_index_map[day]
        if day in self.talks_by_day:
            return day
        return None

    async def ensure_fresh(self) -> None:
        if self.is_stale:
            await self._fetch()

    async def _fetch(self) -> None:
        async with httpx.AsyncClient() as client:
            resp = await client.get(SCHEDULE_URL, timeout=30.0)
            resp.raise_for_status()
            self._raw_data = resp.json()
        self._last_fetch = time.time()
        self._build_indexes()

    def _build_indexes(self) -> None:
        schedule = self._raw_data["schedule"]
        self.conference = schedule["conference"]

        self.talks_by_day = {}
        self.talks_by_track = {}
        self.talks_by_code = {}
        self.speakers = {}
        self._day_index_map = {}

        for day in self.conference["days"]:
            date_str = day["date"]
            self._day_index_map[str(day["index"])] = date_str
            day_talks = []
            for room_name, talks in day["rooms"].items():
                for talk in talks:
                    day_talks.append(talk)

                    # Index by code
                    self.talks_by_code[talk["code"]] = talk

                    # Index by track
                    track = talk.get("track")
                    if track:
                        key = track.lower()
                        self.talks_by_track.setdefault(key, []).append(talk)

                    # Index speakers
                    for person in talk.get("persons", []):
                        speaker_key = person.get("public_name", person["name"]).lower()
                        if speaker_key not in self.speakers:
                            self.speakers[speaker_key] = {
                                "name": person.get("public_name", person["name"]),
                                "biography": person.get("biography", ""),
                                "avatar": person.get("avatar"),
                                "talks": [],
                            }
                        self.speakers[speaker_key]["talks"].append(talk)

            # Sort by start time
            day_talks.sort(key=lambda t: t["start"])
            self.talks_by_day[date_str] = day_talks


def format_talks_table(talks: list[dict]) -> str:
    if not talks:
        return "No talks found."
    lines = ["| Time | Duration | Title | Room | Track | Type | Speakers |"]
    lines.append("|---|---|---|---|---|---|---|")
    for t in talks:
        speakers = ", ".join(p.get("public_name", p["name"]) for p in t.get("persons", []))
        lines.append(
            f"| {t['start']} | {t['duration']} | {t['title']} | {t['room']} "
            f"| {t.get('track', '-')} | {t.get('type', '-')} | {speakers} |"
        )
    return "\n".join(lines)


def format_talk_detail(talk: dict) -> str:
    speakers = ", ".join(p.get("public_name", p["name"]) for p in talk.get("persons", []))
    lines = [
        f"# {talk['title']}",
    ]
    if talk.get("subtitle"):
        lines.append(f"*{talk['subtitle']}*")
    lines.append("")
    lines.append(f"- **Code:** {talk['code']}")
    lines.append(f"- **Date:** {talk['date']}")
    lines.append(f"- **Time:** {talk['start']} ({talk['duration']})")
    lines.append(f"- **Room:** {talk['room']}")
    lines.append(f"- **Track:** {talk.get('track', '-')}")
    lines.append(f"- **Type:** {talk.get('type', '-')}")
    lines.append(f"- **Language:** {talk.get('language', '-')}")
    lines.append(f"- **Speakers:** {speakers}")
    lines.append("")
    if talk.get("abstract"):
        lines.append("## Abstract")
        lines.append(talk["abstract"])
        lines.append("")
    if talk.get("description"):
        lines.append("## Description")
        lines.append(talk["description"])
        lines.append("")
    for person in talk.get("persons", []):
        lines.append(f"## Speaker: {person.get('public_name', person['name'])}")
        if person.get("biography"):
            lines.append(person["biography"])
        lines.append("")
    if talk.get("links"):
        lines.append("## Links")
        for link in talk["links"]:
            lines.append(f"- [{link.get('title', link['url'])}]({link['url']})")
        lines.append("")
    return "\n".join(lines)


def format_speaker_info(speaker: dict) -> str:
    lines = [f"# {speaker['name']}"]
    lines.append("")
    if speaker.get("biography"):
        lines.append(speaker["biography"])
        lines.append("")
    if speaker.get("avatar"):
        lines.append(f"**Avatar:** {speaker['avatar']}")
        lines.append("")
    lines.append("## Talks")
    lines.append("")
    for talk in speaker["talks"]:
        lines.append(f"- **{talk['title']}** ({talk['start']}, {talk['room']}, {talk.get('track', '-')})")
    return "\n".join(lines)


cache = ScheduleCache()
mcp = FastMCP("EC26 Schedule")


@mcp.tool(annotations={"readOnlyHint": True})
async def get_schedule_overview() -> str:
    """Get an overview of the Engineering Camp 2026 schedule: conference info, days, rooms, and tracks."""
    await cache.ensure_fresh()
    conf = cache.conference
    lines = [
        f"# {conf['title']}",
        "",
        f"- **Dates:** {conf['start']} to {conf['end']}",
        f"- **Days:** {conf['daysCount']}",
        f"- **Timezone:** {conf['time_zone_name']}",
        "",
        "## Rooms",
        "",
    ]
    for room in conf.get("rooms", []):
        cap = f" (capacity: {room['capacity']})" if room.get("capacity") else ""
        lines.append(f"- {room['name']}{cap}")
    lines.append("")
    lines.append("## Tracks")
    lines.append("")
    for track in conf.get("tracks", []):
        lines.append(f"- {track['name']}")
    lines.append("")
    lines.append("## Days")
    lines.append("")
    for date_str, talks in cache.talks_by_day.items():
        rooms_in_day = sorted(set(t["room"] for t in talks))
        tracks_in_day = sorted(set(t["track"] for t in talks if t.get("track")))
        lines.append(f"### {date_str} ({len(talks)} talks)")
        lines.append(f"- **Rooms:** {', '.join(rooms_in_day)}")
        lines.append(f"- **Tracks:** {', '.join(tracks_in_day)}")
        lines.append("")
    return "\n".join(lines)


@mcp.tool(annotations={"readOnlyHint": True})
async def get_talks_by_day(day: str) -> str:
    """Get all talks for a specific day. Pass a date like '2026-04-15' or a day index '1'/'2'/'3' (1=April 15, 2=April 16, 3=April 17)."""
    await cache.ensure_fresh()
    date_str = cache.day_index_to_date(day)
    if date_str is None:
        return f"No talks found for day '{day}'. Valid days: {', '.join(sorted(cache.talks_by_day.keys()))}"
    talks = cache.talks_by_day.get(date_str, [])
    if not talks:
        return f"No talks found for {date_str}."
    return f"## Talks on {date_str}\n\n{format_talks_table(talks)}"


@mcp.tool(annotations={"readOnlyHint": True})
async def get_talks_by_track(track: str) -> str:
    """Get all talks in a track. Uses case-insensitive substring matching, e.g. 'ai' matches 'AI Transformation'."""
    await cache.ensure_fresh()
    query = track.lower()
    matching_talks = []
    matching_tracks = []
    for track_name, talks in cache.talks_by_track.items():
        if query in track_name:
            matching_tracks.append(track_name)
            matching_talks.extend(talks)
    if not matching_talks:
        available = ", ".join(sorted(cache.talks_by_track.keys()))
        return f"No talks found for track '{track}'. Available tracks: {available}"
    matching_talks.sort(key=lambda t: (t.get("date", ""), t["start"]))
    header = f"## Talks in: {', '.join(t.title() for t in matching_tracks)}\n\n"
    return header + format_talks_table(matching_talks)


@mcp.tool(annotations={"readOnlyHint": True})
async def get_talk_details(code: str) -> str:
    """Get full details for a talk by its code (e.g. 'AAAAAA'). Returns title, abstract, description, speakers with bios, schedule info."""
    await cache.ensure_fresh()
    talk = cache.talks_by_code.get(code.upper())
    if talk is None:
        return f"Talk with code '{code}' not found."
    return format_talk_detail(talk)


@mcp.tool(annotations={"readOnlyHint": True})
async def search_talks(query: str) -> str:
    """Search talks by keyword. Searches across title, abstract, speaker names, and type. Case-insensitive."""
    await cache.ensure_fresh()
    q = query.lower()
    results = []
    seen_codes = set()
    for talks in cache.talks_by_day.values():
        for talk in talks:
            if talk["code"] in seen_codes:
                continue
            searchable = " ".join([
                talk.get("title", ""),
                talk.get("subtitle", ""),
                talk.get("abstract", ""),
                talk.get("type", ""),
                " ".join(p.get("public_name", p["name"]) for p in talk.get("persons", [])),
            ]).lower()
            if q in searchable:
                results.append(talk)
                seen_codes.add(talk["code"])
    if not results:
        return f"No talks found matching '{query}'."
    results.sort(key=lambda t: (t.get("date", ""), t["start"]))
    return f"## Search results for '{query}' ({len(results)} matches)\n\n{format_talks_table(results)}"


@mcp.tool(annotations={"readOnlyHint": True})
async def get_speaker_info(name: str) -> str:
    """Get info about a speaker by name. Uses case-insensitive substring matching. Returns bio and list of their talks."""
    await cache.ensure_fresh()
    q = name.lower()
    matches = []
    for speaker_key, speaker in cache.speakers.items():
        if q in speaker_key:
            matches.append(speaker)
    if not matches:
        available = ", ".join(s["name"] for s in cache.speakers.values())
        return f"No speaker found matching '{name}'. Available speakers: {available}"
    parts = [format_speaker_info(s) for s in matches]
    return "\n\n---\n\n".join(parts)


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host=HOST, port=PORT)
