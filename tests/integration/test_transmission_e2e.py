import os
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

pytestmark = [
    pytest.mark.integration
]

from trans_sched.client import TransmissionRPCClient
from trans_sched.service import apply_current_policy

TZ = ZoneInfo("America/Chicago")


def _env_required(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise RuntimeError(f"Missing required env: {name}")
    return val


@pytest.fixture(scope="session")
def live_client() -> TransmissionRPCClient:
    """Build a client from env vars; never hardcode creds in the repo."""
    host = _env_required("TRANS_HOST")
    port = int(os.getenv("TRANS_PORT", "9091"))
    path = os.getenv("TRANS_RPC_PATH", "/transmission/rpc")
    timeout = float(os.getenv("TRANS_TIMEOUT", "5.0"))
    return TransmissionRPCClient(host=host, port=port, path=path, timeout=timeout)


@pytest.fixture
def restore_speed(live_client):
    """Snapshot current limits and restore after test."""
    before = live_client.get_current_session()
    try:
        yield before
    finally:
        live_client.set_speed(up=before["speed_up"], down=before["speed_down"])


def _next_value(v: int) -> int:
    # Choose a small delta to avoid impacting your box; adjust if you prefer.
    return max(1, v + 1)


def test_adapter_roundtrip_sets_and_reads(live_client, restore_speed):
    base = restore_speed  # {"speed_up": int, "speed_down": int}
    new_up = _next_value(base["speed_up"])
    new_down = _next_value(base["speed_down"])

    live_client.set_speed(up=new_up, down=new_down)
    sess = live_client.get_current_session()

    assert sess["speed_up"] == new_up
    assert sess["speed_down"] == new_down


def test_service_apply_current_policy_end_to_end(live_client, restore_speed):
    # Create a schedule that always selects our profile right now.
    schedules = [{"profile": "test", "start": "0:00", "end": "23:59"}]

    new_up = _next_value(restore_speed["speed_up"])
    new_down = _next_value(restore_speed["speed_down"])
    profiles = {"test": {"speed_up": new_up, "speed_down": new_down}}

    # First call should change
    changed1 = apply_current_policy(datetime.now(TZ), schedules, profiles, live_client)
    assert changed1 is True

    # Second call should be idempotent
    changed2 = apply_current_policy(datetime.now(TZ), schedules, profiles, live_client)
    assert changed2 is False

    # Verify server state
    sess = live_client.get_current_session()
    assert sess["speed_up"] == new_up
    assert sess["speed_down"] == new_down
