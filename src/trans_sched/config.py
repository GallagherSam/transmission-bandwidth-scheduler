import os
from pathlib import Path
import yaml

from trans_sched.ports import Config

def load_config(cfg_path: Path):
    # Load the config file
    if not cfg_path.exists():
        raise ValueError(f'Config file not found: {cfg_path}')
    try:
        with cfg_path.open("r", encoding="utf-8") as f:
            cfg: Config = yaml.safe_load(f)
    except Exception as e:
        raise ValueError(f"Failed to load {cfg_path}.")
        
    # Validate scheduled profiles exist
    if not _validate_config_schedules_and_profiles(cfg):
        raise ValueError(f'Unknown profile found in the schedule.')
    
    # Load the transmission config from the environment if needed
    _load_transmission_config(cfg)

    return cfg

def _load_transmission_config(cfg: Config):
    if 'transmission' not in cfg:
        cfg['transmission'] = {}

    transmission_config = {
        'host': os.getenv('TRANS_HOST', cfg['transmission']['host'] if 'host' in cfg['transmission'] else 'localhost'),
        'port': int(os.getenv('TRANS_PORT', cfg['transmission']['port'] if 'port' in cfg['transmission'] else 9191)),
        'username': os.getenv('TRANS_USER', cfg['transmission']['username'] if 'username' in cfg['transmission'] else None),
        'password': os.getenv('TRANS_PASS', cfg['transmission']['password'] if  'password' in cfg['transmission'] else None),
        'path': os.getenv('TRANS_RPC_PATH', cfg['transmission']['path'] if 'path' in cfg['transmission'] else '/transmission/rpc'),
        'timeout': float(os.getenv('TRANS_TIMEOUT', cfg['transmission']['timeout'] if 'timeout' in cfg['transmission'] else 5))
    }

    cfg['transmission'] = transmission_config

def _validate_config_schedules_and_profiles(cfg: Config):
    """
    Validate that all profiles listed in the schedule are defined.
    """
    profiles = set(cfg.get('profiles', {}).keys())
    for s in cfg.get('schedules', []):
        if s.get('profile') not in profiles:
            return False
    return True