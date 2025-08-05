# Transmission Bandwidth Scheduler

A tiny, test-driven CLI that switches your Transmission speed limits based on time of day.
Built with clean seams (policy → service → client), structured logs, and both unit & live integration tests.

[![CI](https://github.com/GallagherSam/transmission-bandwidth-scheduler/actions/workflows/ci.yml/badge.svg)](https://github.com/GallagherSam/transmission-bandwidth-scheduler/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/GallagherSam/transmission-bandwidth-scheduler/branch/master/graph/badge.svg)](https://codecov.io/gh/GallagherSam/transmission-bandwidth-scheduler)

## Why?

Sometimes you want Transmission to be polite during the day and fast at night. This tool reads a simple YAML schedule and applies the corresponding regular speed limits via Transmission’s RPC.

Designed to be cron-friendly, idempotent, and easy to debug.

## Features:

    ✅ Time-window policy with clear boundary rules ([start, end), midnight wrap supported)
    ✅ Idempotent apply: only updates when a change is needed
    ✅ Configurable via YAML with env overrides (TRANS_*)
    ✅ Structured logging with structlog (console or JSON)
    ✅ Small surface area: one CLI apply-now
    ✅ Tests: fast unit tests + optional live integration test

## Install

Requirements: Python >= 3.11, Transmission with RPC enabled.

```bash
# clone
git clone https://github.com/GallagherSam/transmission-bandwidth-scheduler.git
cd <repo>

# create venv
python -m venv .venv
source .venv/bin/activate

# install
pip install -e ".[dev]"   # dev extras include pytest/coverage, optional
```

## Configuration

Create a YAML file (e.g., `/etc/transmission-bandwidth-scheduler/config.yaml`):

```yaml
timezone: "America/Chicago"

profiles:
  day:
    speed_up: 2000   # KB/s
    speed_down: 8000
  night:
    speed_up: 1000
    speed_down: 1000

schedules:
  - profile: night
    start: "23:00"
    end: "7:00"    # wraps past midnight
  - profile: day
    start: "7:00"
    end: "23:00"

# Optional: Transmission connection (env can override)
transmission:
  host: 192.168.1.50
  port: 9091
  username: transmission
  password: secret
  path: /transmission/rpc
  timeout: 5.0

```

**Boundary semantics:** intervals are [start, end) (inclusive of start, exclusive of end).
Midnight wrap is supported (e.g., 23:00 → 7:00).


## Environment Overrides

Environment variables override YAML:

| Var              | Meaning               | Default             |
| ---------------- | --------------------- | ------------------- |
| `TRANS_HOST`     | RPC host              | `localhost`         |
| `TRANS_PORT`     | RPC port              | `9091`              |
| `TRANS_USER`     | RPC username          | `None`              |
| `TRANS_PASS`     | RPC password          | `None`              |
| `TRANS_RPC_PATH` | RPC path              | `/transmission/rpc` |
| `TRANS_TIMEOUT`  | RPC timeout (seconds) | `5.0`               |
| `LOG_LEVEL`      | `DEBUG`/`INFO`/…      | `INFO`              |
| `LOG_FORMAT`     | `console` or `json`   | `console`           |

## Usage

Run once:

```bash
transmission-bandwidth-scheduler apply-now --config /etc/transmission-bandwidth-scheduler/config.yaml
```

Example output:

```bash
2025-08-05T07:05:00 [info] applied_profile profile=day previous_up=100 previous_down=100 target_up=2000 target_down=8000
```

## Packaging

Zipapp (requires Python on server to run this)

```bash
pip install shiv
shiv -c transmission-bandwidth-scheduler -o dist/transmission-bandwidth-scheduler.pyz .
```

## Development

Run tests

```bash
# unit tests + coverage
pytest -q -m "not integration" --cov=src --cov-report=term
```

