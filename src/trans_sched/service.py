from datetime import datetime
from typing import Sequence, Dict, Any
import structlog

from trans_sched.policy import choose_profile
from trans_sched.ports import TransmissionClient, Session

log = structlog.get_logger(__name__)

def apply_current_policy(now: datetime, schedule: Sequence[Dict[str, Any]], profiles: Dict[str, Any], client: TransmissionClient) -> bool:
    desired_profile_name = choose_profile(now, schedule)

    if desired_profile_name in profiles:
        desired_profile: Session = profiles[desired_profile_name]
    else:
        raise ValueError(f'No matching profile found for {desired_profile_name}.')

    current_profile = client.get_current_session()    
    prev_up, prev_down = current_profile['speed_up'], current_profile['speed_down']
    target_up, target_down = desired_profile['speed_up'], desired_profile['speed_down']

    need_change = (prev_up != target_up) or (prev_down != target_down)
    if not need_change:
        log.info('no_change', profile=desired_profile_name, current_up=prev_up, current_down=prev_down)
        return False
    
    client.set_speed(target_up, target_down)
    log.info('applied_profile', profile=desired_profile_name, previous_up=prev_up, previous_down=prev_down, target_up=target_up, target_down=target_down)
    return True
