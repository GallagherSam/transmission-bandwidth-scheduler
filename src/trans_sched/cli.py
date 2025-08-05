from __future__ import annotations
import argparse
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Optional

from trans_sched.config import load_config
from trans_sched.client import TransmissionRPCClient
from trans_sched.service import apply_current_policy
from trans_sched.logging_setup import setup_logging

def run(argv: Optional[List[str]] = None) -> int:
    setup_logging()
    parser = argparse.ArgumentParser(prog="trans-scheduler")
    sub = parser.add_subparsers(dest="command", required=True)

    p_apply = sub.add_parser("apply-now", help="Apply the current scheduled profile to Transmission")
    p_apply.add_argument("--config", required=True, type=Path, help="Path to YAML config.")

    args = parser.parse_args(argv)

    if args.command == "apply-now":
        return _apply_now(args.config)

    return 1

def _apply_now(config_path: Path) -> int:
    cfg = load_config(config_path)

    tz = ZoneInfo(cfg["timezone"])
    now = datetime.now(tz)

    tx_kwargs = {k: v for k, v in cfg.get('transmission', {}).items() if v is not None}
    client = TransmissionRPCClient(**tx_kwargs)
    changed = apply_current_policy(now, cfg["schedules"], cfg["profiles"], client)

    return 0

def main() -> None:
    raise SystemExit(run())