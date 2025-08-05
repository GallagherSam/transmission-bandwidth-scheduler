from __future__ import annotations
from datetime import datetime, time
from typing import Sequence, Dict, Any

def _parse_hhmm(s: str) -> time:
    """
    Accepts '7:00' or '07:00' -> datetime.time
    (We avoid time.fromisoformat because it rejects '7:00')
    """
    h_str, m_str = s.strip().split(':')
    return time(hour=int(h_str), minute=int(m_str))

def choose_profile(now: datetime, schedule: Sequence[Dict[str, Any]]) -> str:
    """
    Returns the first profile whose window contains `now.time()`.

    Rule: intervals are [from, to] - inclusive of 'from' and exclusive of 'to'.
    """
    t = now.timetz().replace(tzinfo=None)

    for rule in schedule:
        start = _parse_hhmm(rule['start'])
        end = _parse_hhmm(rule['end'])

        if start <= end:
            in_window = (start <= t < end)
        else:
            # Wrap past midnight
            in_window = (t >= start) or (t < end)
        
        if in_window:
            return rule['profile']
    
    raise ValueError('No matching schedule for current time.')