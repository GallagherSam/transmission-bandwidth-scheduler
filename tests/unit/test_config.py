from textwrap import dedent
from pathlib import Path

from trans_sched.config import load_config

def test_loads_profiles_and_schedules_from_yaml(tmp_path: Path):
    cfg = dedent("""
timezone: America/Chicago
profiles:
  night:
    speed_up: 1000
    speed_down: 1000
  day:
    speed_up: 10
    speed_down: 10
schedules:
  - profile: night
    start: "23:00"
    end: "7:00"
  - profile: day
    start: "7:00"
    end: "23:00"
    """)
    p = tmp_path / "config.yaml"
    p.write_text(cfg)

    result = load_config(p)

    assert result["timezone"] == "America/Chicago"
    assert result["profiles"]["night"] == {"speed_up": 1000, "speed_down": 1000}
    assert result["schedules"][0] == {"profile": "night", "start": "23:00", "end": "7:00"}

def test_raises_if_unable_to_load_yaml():
    p = Path('/path/to/nowhere.yaml')
    try:
        load_config(p)
        assert False, "expected ValueError"
    except ValueError as e:
        assert "config file not found" in str(e).lower()


def test_raises_if_schedule_references_unknown_profile(tmp_path: Path):
    cfg = dedent("""
    profiles:
      day: { speed_up: 10, speed_down: 10 }
    schedules:
      - profile: night
        start: "23:00"
        end: "7:00"
    """)
    p = tmp_path / "bad.yaml"
    p.write_text(cfg)

    try:
        load_config(p)
        assert False, "expected ValueError"
    except ValueError as e:
        assert "unknown profile" in str(e).lower()

def test_loads_transmission_settings_from_yaml(tmp_path: Path):
    cfg = dedent("""
    timezone: America/Chicago
    profiles:
      day: { speed_up: 10, speed_down: 10 }
    schedules:
      - profile: day
        start: "7:00"
        end: "23:00"

    transmission:
      host: 192.168.1.20
      port: 9091
      username: trans
      password: secret
      path: /transmission/rpc
      timeout: 7.5
    """)
    p = tmp_path / "config.yaml"
    p.write_text(cfg)

    result = load_config(p)

    assert result["transmission"] == {
        "host": "192.168.1.20",
        "port": 9091,
        "username": "trans",
        "password": "secret",
        "path": "/transmission/rpc",
        "timeout": 7.5,
    }

def test_env_overrides_and_defaults(tmp_path, monkeypatch):
    # YAML without transmission section
    cfg = dedent("""
    timezone: America/Chicago
    profiles:
      day: { speed_up: 10, speed_down: 10 }
    schedules:
      - profile: day
        start: "7:00"
        end: "23:00"
    transmission:
      host: 1.1.1.1
    """)
    p = tmp_path / "config.yaml"
    p.write_text(cfg)

    # Set env vars
    monkeypatch.setenv("TRANS_HOST", "10.0.0.5")
    monkeypatch.setenv("TRANS_PORT", "9191")
    monkeypatch.setenv("TRANS_USER", "alice")
    monkeypatch.setenv("TRANS_PASS", "pw")
    monkeypatch.setenv("TRANS_RPC_PATH", "/rpc")
    monkeypatch.setenv("TRANS_TIMEOUT", "4.0")

    result = load_config(p)

    assert result["transmission"] == {
        "host": "10.0.0.5",
        "port": 9191,
        "username": "alice",
        "password": "pw",
        "path": "/rpc",
        "timeout": 4.0,
    }