from datetime import datetime, timezone, timedelta

from server.time_utils import utc_timestamp
from server.routes.room_routes import serialize_announcement
from server.routes.exam_draft_routes import serialize as serialize_draft


def test_database_utc_timestamp_has_explicit_timezone():
    assert utc_timestamp(datetime(2026, 10, 21, 20, 49, 38)) == '2026-10-21T20:49:38Z'
    assert utc_timestamp(datetime(2026, 10, 22, 3, 49, 38, tzinfo=timezone(timedelta(hours=7)))) == '2026-10-21T20:49:38Z'


def test_announcement_and_draft_expose_timezone():
    created = datetime(2026, 10, 21, 20, 49, 38)
    announcement = serialize_announcement({'created_at': created, 'updated_at': created, 'attachments': None})
    draft = serialize_draft({'created_at': created, 'updated_at': created, 'questions': '[]'})
    assert announcement['created_at'].endswith('Z')
    assert announcement['updated_at'].endswith('Z')
    assert draft['created_at'].endswith('Z')
    assert draft['updated_at'].endswith('Z')
