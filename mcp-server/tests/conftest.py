import pytest

SAMPLE_SCHEDULE = {
    "schedule": {
        "conference": {
            "acronym": "ec26",
            "title": "Engineering Camp 2026",
            "start": "2026-04-15",
            "end": "2026-04-17",
            "daysCount": 3,
            "timeslot_duration": "00:05",
            "time_zone_name": "Europe/Berlin",
            "rooms": [
                {"name": "Plenum", "guid": "room-1", "capacity": 300},
                {"name": "Konferenz 1", "guid": "room-2", "capacity": 75},
            ],
            "tracks": [
                {"name": "AI Transformation", "color": "#ff0000"},
                {"name": "Cloud Transformation", "color": "#0000ff"},
            ],
            "days": [
            {
                "index": 1,
                "date": "2026-04-15",
                "day_start": "2026-04-15T09:00:00+02:00",
                "day_end": "2026-04-15T21:00:00+02:00",
                "rooms": {
                    "Plenum": [
                        {
                            "guid": "talk-1",
                            "code": "AAAAAA",
                            "id": 1,
                            "date": "2026-04-15T09:00:00+02:00",
                            "start": "09:00",
                            "duration": "00:45",
                            "room": "Plenum",
                            "slug": "ec26-1-opening-keynote",
                            "title": "Opening Keynote",
                            "subtitle": "",
                            "track": "AI Transformation",
                            "type": "Keynote",
                            "language": "de",
                            "abstract": "Welcome to EC26! This keynote covers AI trends.",
                            "description": "A deep dive into current AI transformation.",
                            "persons": [
                                {
                                    "code": "SPKR01",
                                    "name": "Anna Schmidt",
                                    "public_name": "Anna Schmidt",
                                    "biography": "AI researcher at QAware.",
                                    "avatar": "https://example.com/anna.jpg",
                                    "guid": "person-1",
                                }
                            ],
                            "links": [],
                            "attachments": [],
                        },
                        {
                            "guid": "talk-2",
                            "code": "BBBBBB",
                            "id": 2,
                            "date": "2026-04-15T10:00:00+02:00",
                            "start": "10:00",
                            "duration": "00:30",
                            "room": "Plenum",
                            "slug": "ec26-2-cloud-native",
                            "title": "Cloud Native Patterns",
                            "subtitle": "Best practices",
                            "track": "Cloud Transformation",
                            "type": "Talk lang",
                            "language": "de",
                            "abstract": "Modern cloud native architecture patterns.",
                            "description": "",
                            "persons": [
                                {
                                    "code": "SPKR02",
                                    "name": "Max Müller",
                                    "public_name": "Max Müller",
                                    "biography": "Cloud architect.",
                                    "avatar": None,
                                    "guid": "person-2",
                                }
                            ],
                            "links": [],
                            "attachments": [],
                        },
                    ],
                    "Konferenz 1": [
                        {
                            "guid": "talk-3",
                            "code": "CCCCCC",
                            "id": 3,
                            "date": "2026-04-15T10:00:00+02:00",
                            "start": "10:00",
                            "duration": "01:30",
                            "room": "Konferenz 1",
                            "slug": "ec26-3-ai-workshop",
                            "title": "Hands-on AI Workshop",
                            "subtitle": "",
                            "track": "AI Transformation",
                            "type": "Workshop",
                            "language": "de",
                            "abstract": "Build your first AI agent.",
                            "description": "Practical workshop on building AI agents with Claude.",
                            "persons": [
                                {
                                    "code": "SPKR01",
                                    "name": "Anna Schmidt",
                                    "public_name": "Anna Schmidt",
                                    "biography": "AI researcher at QAware.",
                                    "avatar": "https://example.com/anna.jpg",
                                    "guid": "person-1",
                                }
                            ],
                            "links": [],
                            "attachments": [],
                        }
                    ],
                },
            },
            {
                "index": 2,
                "date": "2026-04-16",
                "day_start": "2026-04-16T09:00:00+02:00",
                "day_end": "2026-04-16T21:00:00+02:00",
                "rooms": {
                    "Plenum": [
                        {
                            "guid": "talk-4",
                            "code": "DDDDDD",
                            "id": 4,
                            "date": "2026-04-16T09:00:00+02:00",
                            "start": "09:00",
                            "duration": "00:20",
                            "room": "Plenum",
                            "slug": "ec26-4-lightning",
                            "title": "AI in Production",
                            "subtitle": "",
                            "track": "AI Transformation",
                            "type": "Lightning Talk",
                            "language": "de",
                            "abstract": "Running AI workloads in production.",
                            "description": "",
                            "persons": [
                                {
                                    "code": "SPKR02",
                                    "name": "Max Müller",
                                    "public_name": "Max Müller",
                                    "biography": "Cloud architect.",
                                    "avatar": None,
                                    "guid": "person-2",
                                }
                            ],
                            "links": [],
                            "attachments": [],
                        }
                    ]
                },
            },
            ],
        },
    }
}


@pytest.fixture
def sample_schedule():
    return SAMPLE_SCHEDULE
