from datetime import datetime
from zoneinfo import ZoneInfo

from trans_sched.service import apply_current_policy

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
PROFILES = {
    "night": {
        "speed_up": 1000,
        "speed_down": 1000
    },
    "day": {
        "speed_up": 10,
        "speed_down": 10
    }
}

class FakeClient:
    def __init__(self, session=None):
        if session is None:
            session = {
                "speed_up": 100,
                "speed_down": 100
            }
        self._session = dict(session)
        self.calls = []
    
    def get_current_session(self):
        return dict(self._session)

    def set_speed(self, up: int | None = None, down: int | None = None):
        if up is not None:
            self._session["speed_up"] = up
        if down is not None:
            self._session["speed_down"] = down
        self.calls.append(("set_speed", up, down))

def test_apply_changes_when_needed():
    now = datetime(2025, 8, 5, 0, 0, tzinfo=TZ) # midnight -> night profile
    client = FakeClient(session={"speed_up": 100, "speed_down": 100})

    changed = apply_current_policy(now, SCHEDULE, PROFILES, client)

    assert changed is True
    assert client.calls == [("set_speed", 1000, 1000)]

def test_idempotent_when_already_in_target_state():
    now = datetime(2025, 8, 5, 0, 0, tzinfo=TZ) # midnight -> night profile
    client = FakeClient(session={"speed_up": 1000, "speed_down": 1000})

    changed = apply_current_policy(now, SCHEDULE, PROFILES, client)

    assert changed is False
    assert client.calls == []
