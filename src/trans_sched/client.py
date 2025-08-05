from __future__ import annotations
from typing import Optional

from transmission_rpc import Client as _TxClient
from trans_sched.ports import TransmissionClient, Session

class TransmissionRPCClient(TransmissionClient):
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 9091,
        username: Optional[str] = None,
        password: Optional[str] = None,
        path: str = '/transmission/rpc',
        timeout: float = 5.0
    ) -> None:
        self._c = _TxClient(
            host=host,
            port=port,
            username=username,
            password=password,
            path=path,
            timeout=timeout
        )

    def get_current_session(self) -> Session:
        s = self._c.get_session()
        return {
            "speed_up": int(s.speed_limit_up or 0),
            "speed_down": int(s.speed_limit_down or 0)
        }
    
    def set_speed(self, up: Optional[int] = None, down: Optional[int] = None):
        kwargs = {}
        if up is not None:
            kwargs["speed_limit_up"] = int(up)
            kwargs["speed_limit_up_enabled"] = True
        if down is not None:
            kwargs["speed_limit_down"] = int(down)
            kwargs["speed_limit_down_enabled"] = True
        if kwargs:
            self._c.set_session(**kwargs)