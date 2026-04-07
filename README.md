# EC26 Schedule MCP Server

MCP server that exposes the [Engineering Camp 2026](https://ec26.qaware.de) schedule as tools for AI agents.

## Setup

```bash
pip install -e ".[dev]"
```

## Run

```bash
python server.py
```

The server starts on `http://0.0.0.0:8000` with SSE transport.

## Configuration

| Env Variable | Default | Description |
|---|---|---|
| `CACHE_TTL_SECONDS` | `900` | How often to refresh schedule data (seconds) |
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `8000` | Listen port |

## Tools

| Tool | Description |
|---|---|
| `get_schedule_overview` | Conference overview: dates, rooms, tracks, per-day summary |
| `get_talks_by_day` | All talks for a day (by date or index 1/2/3) |
| `get_talks_by_track` | All talks in a track (substring match) |
| `get_talk_details` | Full talk details by code |
| `search_talks` | Search talks by keyword |
| `get_speaker_info` | Speaker bio and talks (substring match) |

## MCP Client Configuration

Add to your MCP client config:

```json
{
  "mcpServers": {
    "ec26-schedule": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

## Development

```bash
python -m pytest tests/ -v
```
