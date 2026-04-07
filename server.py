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

        for day in schedule["days"]:
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


if __name__ == "__main__":
    mcp.run(transport="sse", host=HOST, port=PORT)
