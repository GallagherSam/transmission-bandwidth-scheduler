from typing import Protocol, Optional, Dict, TypedDict, runtime_checkable, List

class Session(TypedDict):
    speed_up: int
    speed_down: int

class Schedule(TypedDict):
    profile: str
    start: str
    end: str

class TransmissionSettings(TypedDict, total=False):
    host: str
    port: int
    username: Optional[str]
    password: Optional[str]
    path: str
    timeout: float

class Config(TypedDict):
    timezone: str
    profiles: Dict[str, Session]
    schedules: List[Schedule]

@runtime_checkable
class TransmissionClient(Protocol):
    def get_current_session(self) -> dict: ...
    def set_speed(self, up: Optional[int] = None, down: Optional[int] = None) -> None: ...