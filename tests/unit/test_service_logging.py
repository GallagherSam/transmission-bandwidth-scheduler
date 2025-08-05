from datetime import datetime
from zoneinfo import ZoneInfo
from structlog.testing import capture_logs

from trans_sched.service import apply_current_policy

TZ = ZoneInfo("America/Chicago")

SCHEDULE = [
    {"profile": "night", "start": "23:00", "end": "7:00"},
    {"profile": "day",   "start": "7:00",  "end": "23:00"},
]
PROFILES = {
    "night": {"speed_up": 1000, "speed_down": 1000},
    "day":   {"speed_up": 10,   "speed_down": 10},
}

class FakeClient:
    def __init__(self, session):
        self._session = dict(session)
        self.calls = []
    def get_current_session(self):
        return dict(self._session)
    def set_speed(self, up=None, down=None):
        if up is not None: self._session["speed_up"] = up
        if down is not None: self._session["speed_down"] = down
        self.calls.append(("set_speed", up, down))


def test_logs_applied_profile_when_change_needed():
    now = datetime(2025, 8, 5, 0, 0, tzinfo=TZ)  # -> night
    client = FakeClient({"speed_up": 100, "speed_down": 100})

    with capture_logs() as logs:
        changed = apply_current_policy(now, SCHEDULE, PROFILES, client)

    assert changed is True
    # Find our info event
    evts = [e for e in logs if e.get("event") == "applied_profile"]
    assert evts, f"expected applied_profile log, got: {logs}"
    evt = evts[-1]
    assert evt["profile"] == "night"
    assert evt["target_up"] == 1000 and evt["target_down"] == 1000
    assert evt["previous_up"] == 100 and evt["previous_down"] == 100


def test_logs_no_change_when_already_in_state():
    now = datetime(2025, 8, 5, 0, 0, tzinfo=TZ)  # -> night
    client = FakeClient({"speed_up": 1000, "speed_down": 1000})

    with capture_logs() as logs:
        changed = apply_current_policy(now, SCHEDULE, PROFILES, client)

    assert changed is False
    evts = [e for e in logs if e.get("event") == "no_change"]
    assert evts, f"expected no_change log, got: {logs}"
    assert evts[-1]["profile"] == "night"