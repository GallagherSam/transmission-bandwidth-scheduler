import types
from trans_sched.client import TransmissionRPCClient

class FakeLibClient:
    def __init__(self):
        sess = types.SimpleNamespace(
            speed_limit_up=50,
            speed_limit_down=1200
        )
        self._session = sess
        self.set_calls = []
    
    def get_session(self):
        return self._session

    def set_session(self, **kwargs):
        self.set_calls.append(kwargs)

def test_adapter_reads_speed_limits(monkeypatch):
    fake = FakeLibClient()
    monkeypatch.setattr('trans_sched.client._TxClient', lambda **_: fake)
    
    c = TransmissionRPCClient()
    s = c.get_current_session()
    assert s == {"speed_up": 50, "speed_down": 1200}

def test_adapter_writes_speed_limits(monkeypatch):
    fake = FakeLibClient()
    monkeypatch.setattr('trans_sched.client._TxClient', lambda **_: fake)

    c = TransmissionRPCClient()
    c.set_speed(up=500, down=500)

    assert fake.set_calls == [{
        "speed_limit_up": 500, "speed_limit_up_enabled": True,
        "speed_limit_down": 500, "speed_limit_down_enabled": True
    }]
