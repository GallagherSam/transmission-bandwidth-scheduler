# tests/unit/test_cli_env.py
from pathlib import Path
from textwrap import dedent

from trans_sched.cli import run

def test_cli_constructs_client_with_settings(monkeypatch, tmp_path: Path):
    cfg = dedent("""
    timezone: America/Chicago
    profiles:
      day: { speed_up: 10, speed_down: 10 }
    schedules:
      - profile: day
        start: "7:00"
        end: "23:00"
    transmission:
      host: 1.2.3.4
      port: 9191
      username: alice
      password: pw
      path: /rpc
      timeout: 4.0
    """)
    p = tmp_path / "c.yaml"
    p.write_text(cfg)

    captured = {}
    def fake_client(**kwargs):
        captured.update(kwargs)
        class Dummy: pass
        return Dummy()

    def fake_apply(now, schedules, profiles, client):
        return True

    monkeypatch.setattr("trans_sched.cli.TransmissionRPCClient", fake_client)
    monkeypatch.setattr("trans_sched.cli.apply_current_policy", fake_apply)

    code = run(["apply-now", "--config", str(p)])
    assert code == 0
    assert captured == {
        "host": "1.2.3.4",
        "port": 9191,
        "username": "alice",
        "password": "pw",
        "path": "/rpc",
        "timeout": 4.0,
    }
