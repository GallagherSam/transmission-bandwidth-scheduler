from datetime import datetime
from zoneinfo import ZoneInfo

from trans_sched.policy import choose_profile

TZ = ZoneInfo("America/Chicago")
SCHEDULE = [
        {
            "profile": "night",
            "start": "23:00",
            "end": "7:00",
        },
        {
            "profile": "day",
            "start": "7:00",
            "end": "23:00"
        }
]

def test_midnight_uses_night_profile():
    now = datetime(2025, 8, 5, 0, 0, tzinfo=TZ)
    assert choose_profile(now, SCHEDULE) == "night"

def test_noon_uses_day_profile():
    now = datetime(2025, 8, 5, 12, 0, tzinfo=TZ)
    assert choose_profile(now, SCHEDULE) == "day"

def test_boundary_start_is_inclusive_for_day():
    assert choose_profile(datetime(2025, 8, 5, 7, 0, tzinfo=TZ), SCHEDULE) == "day"

def test_boundary_end_is_exclusive_for_day_start_of_night_is_inclusive():
    assert choose_profile(datetime(2025, 8, 5, 23, 0, tzinfo=TZ), SCHEDULE) == "night"