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


cache = ScheduleCache()
mcp = FastMCP("EC26 Schedule")


if __name__ == "__main__":
    mcp.run(transport="sse", host=HOST, port=PORT)
