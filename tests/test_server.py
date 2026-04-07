import time
import pytest
from unittest.mock import AsyncMock, patch
from server import ScheduleCache


@pytest.fixture
def cache(sample_schedule):
    c = ScheduleCache(cache_ttl_seconds=900)
    c._raw_data = sample_schedule
    c._last_fetch = time.time()
    c._build_indexes()
    return c


class TestScheduleCache:
    def test_build_indexes_creates_talks_by_day(self, cache):
        assert "2026-04-15" in cache.talks_by_day
        assert "2026-04-16" in cache.talks_by_day
        assert len(cache.talks_by_day["2026-04-15"]) == 3
        assert len(cache.talks_by_day["2026-04-16"]) == 1

    def test_build_indexes_creates_talks_by_track(self, cache):
        assert "ai transformation" in cache.talks_by_track
        assert "cloud transformation" in cache.talks_by_track
        assert len(cache.talks_by_track["ai transformation"]) == 3
        assert len(cache.talks_by_track["cloud transformation"]) == 1

    def test_build_indexes_creates_speakers(self, cache):
        assert "anna schmidt" in cache.speakers
        assert "max müller" in cache.speakers
        assert len(cache.speakers["anna schmidt"]["talks"]) == 2
        assert len(cache.speakers["max müller"]["talks"]) == 2

    def test_build_indexes_creates_talks_by_code(self, cache):
        assert "AAAAAA" in cache.talks_by_code
        assert cache.talks_by_code["AAAAAA"]["title"] == "Opening Keynote"

    def test_cache_is_stale_when_expired(self, cache):
        cache._last_fetch = time.time() - 1000
        cache._cache_ttl_seconds = 900
        assert cache.is_stale is True

    def test_cache_is_fresh_when_not_expired(self, cache):
        cache._last_fetch = time.time()
        cache._cache_ttl_seconds = 900
        assert cache.is_stale is False

    def test_cache_is_stale_when_never_fetched(self):
        c = ScheduleCache(cache_ttl_seconds=900)
        assert c.is_stale is True

    def test_day_index_mapping(self, cache):
        assert cache.day_index_to_date("1") == "2026-04-15"
        assert cache.day_index_to_date("2") == "2026-04-16"
        assert cache.day_index_to_date("2026-04-15") == "2026-04-15"


from server import format_talks_table, format_talk_detail, format_speaker_info


class TestMarkdownFormatters:
    def test_format_talks_table_produces_markdown_table(self, cache):
        talks = cache.talks_by_day["2026-04-15"]
        result = format_talks_table(talks)
        assert "| Time" in result
        assert "Opening Keynote" in result
        assert "Cloud Native Patterns" in result
        assert "Hands-on AI Workshop" in result
        # Should contain table separator
        assert "|---|" in result

    def test_format_talks_table_empty_list(self):
        result = format_talks_table([])
        assert "No talks found" in result

    def test_format_talk_detail(self, cache):
        talk = cache.talks_by_code["AAAAAA"]
        result = format_talk_detail(talk)
        assert "# Opening Keynote" in result
        assert "Anna Schmidt" in result
        assert "AI researcher" in result
        assert "09:00" in result
        assert "Plenum" in result
        assert "AI Transformation" in result
        assert "AAAAAA" in result

    def test_format_speaker_info(self, cache):
        speaker = cache.speakers["anna schmidt"]
        result = format_speaker_info(speaker)
        assert "# Anna Schmidt" in result
        assert "AI researcher" in result
        assert "Opening Keynote" in result
        assert "Hands-on AI Workshop" in result


class TestTools:
    @pytest.mark.asyncio
    async def test_get_schedule_overview(self, cache):
        from server import get_schedule_overview, cache as server_cache
        server_cache._raw_data = cache._raw_data
        server_cache._last_fetch = cache._last_fetch
        server_cache._build_indexes()
        result = await get_schedule_overview()
        assert "Engineering Camp 2026" in result
        assert "2026-04-15" in result
        assert "2026-04-16" in result
        assert "Plenum" in result
        assert "AI Transformation" in result

    @pytest.mark.asyncio
    async def test_get_talks_by_day_with_date(self, cache):
        from server import get_talks_by_day, cache as server_cache
        server_cache._raw_data = cache._raw_data
        server_cache._last_fetch = cache._last_fetch
        server_cache._build_indexes()
        result = await get_talks_by_day("2026-04-15")
        assert "Opening Keynote" in result
        assert "Cloud Native Patterns" in result
        assert "Hands-on AI Workshop" in result

    @pytest.mark.asyncio
    async def test_get_talks_by_day_with_index(self, cache):
        from server import get_talks_by_day, cache as server_cache
        server_cache._raw_data = cache._raw_data
        server_cache._last_fetch = cache._last_fetch
        server_cache._build_indexes()
        result = await get_talks_by_day("1")
        assert "Opening Keynote" in result

    @pytest.mark.asyncio
    async def test_get_talks_by_day_not_found(self, cache):
        from server import get_talks_by_day, cache as server_cache
        server_cache._raw_data = cache._raw_data
        server_cache._last_fetch = cache._last_fetch
        server_cache._build_indexes()
        result = await get_talks_by_day("2026-12-31")
        assert "No talks found" in result

    @pytest.mark.asyncio
    async def test_get_talks_by_track(self, cache):
        from server import get_talks_by_track, cache as server_cache
        server_cache._raw_data = cache._raw_data
        server_cache._last_fetch = cache._last_fetch
        server_cache._build_indexes()
        result = await get_talks_by_track("ai")
        assert "Opening Keynote" in result
        assert "Hands-on AI Workshop" in result
        assert "AI in Production" in result

    @pytest.mark.asyncio
    async def test_get_talks_by_track_not_found(self, cache):
        from server import get_talks_by_track, cache as server_cache
        server_cache._raw_data = cache._raw_data
        server_cache._last_fetch = cache._last_fetch
        server_cache._build_indexes()
        result = await get_talks_by_track("quantum")
        assert "No talks found" in result

    @pytest.mark.asyncio
    async def test_get_talk_details(self, cache):
        from server import get_talk_details, cache as server_cache
        server_cache._raw_data = cache._raw_data
        server_cache._last_fetch = cache._last_fetch
        server_cache._build_indexes()
        result = await get_talk_details("AAAAAA")
        assert "# Opening Keynote" in result
        assert "Anna Schmidt" in result
        assert "AI researcher" in result
        assert "09:00" in result

    @pytest.mark.asyncio
    async def test_get_talk_details_not_found(self, cache):
        from server import get_talk_details, cache as server_cache
        server_cache._raw_data = cache._raw_data
        server_cache._last_fetch = cache._last_fetch
        server_cache._build_indexes()
        result = await get_talk_details("ZZZZZZ")
        assert "not found" in result.lower()

    @pytest.mark.asyncio
    async def test_search_talks_by_title(self, cache):
        from server import search_talks, cache as server_cache
        server_cache._raw_data = cache._raw_data
        server_cache._last_fetch = cache._last_fetch
        server_cache._build_indexes()
        result = await search_talks("keynote")
        assert "Opening Keynote" in result

    @pytest.mark.asyncio
    async def test_search_talks_by_speaker(self, cache):
        from server import search_talks, cache as server_cache
        server_cache._raw_data = cache._raw_data
        server_cache._last_fetch = cache._last_fetch
        server_cache._build_indexes()
        result = await search_talks("müller")
        assert "Cloud Native Patterns" in result
        assert "AI in Production" in result

    @pytest.mark.asyncio
    async def test_search_talks_by_abstract(self, cache):
        from server import search_talks, cache as server_cache
        server_cache._raw_data = cache._raw_data
        server_cache._last_fetch = cache._last_fetch
        server_cache._build_indexes()
        result = await search_talks("agent")
        assert "Hands-on AI Workshop" in result

    @pytest.mark.asyncio
    async def test_search_talks_no_results(self, cache):
        from server import search_talks, cache as server_cache
        server_cache._raw_data = cache._raw_data
        server_cache._last_fetch = cache._last_fetch
        server_cache._build_indexes()
        result = await search_talks("quantum computing")
        assert "No talks found" in result

    @pytest.mark.asyncio
    async def test_get_speaker_info(self, cache):
        from server import get_speaker_info, cache as server_cache
        server_cache._raw_data = cache._raw_data
        server_cache._last_fetch = cache._last_fetch
        server_cache._build_indexes()
        result = await get_speaker_info("anna")
        assert "# Anna Schmidt" in result
        assert "AI researcher" in result
        assert "Opening Keynote" in result
        assert "Hands-on AI Workshop" in result

    @pytest.mark.asyncio
    async def test_get_speaker_info_not_found(self, cache):
        from server import get_speaker_info, cache as server_cache
        server_cache._raw_data = cache._raw_data
        server_cache._last_fetch = cache._last_fetch
        server_cache._build_indexes()
        result = await get_speaker_info("nobody")
        assert "No speaker found" in result
