from pathlib import Path
from textwrap import dedent

from trans_sched.cli import run

def test_cli_apply_now_reads_config_and_calls_services(monkeypatch, tmp_path: Path):
    cfg = dedent("""
    timezone: America/Chicago
    profiles:
      day: { speed_up: 10, speed_down: 10 }
    schedules:
      - profile: day
        start: "7:00"
        end: "23:00"
    """)
    p = tmp_path / "c.yaml"
    p.write_text(cfg)

    called = {}
    def fake_apply_current_policy(now, schedules, profiles, client):
        called["schedules_ok"] = (schedules and schedules[0]["profile"] == "day")
        called["profiles_ok"] = ("day" in profiles and profiles["day"]["speed_up"] == 10)
        return True
    
    class DummyClient:
        pass

    monkeypatch.setattr("trans_sched.cli.apply_current_policy", fake_apply_current_policy)
    monkeypatch.setattr("trans_sched.cli.TransmissionRPCClient", lambda **_: DummyClient())

    code = run(["apply-now", "--config", str(p)])
    assert code == 0
    assert called.get("schedules_ok") is True
    assert called.get("profiles_ok") is True