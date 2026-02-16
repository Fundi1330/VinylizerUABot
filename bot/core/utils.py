from bot.config import config
from json import loads
from pathlib import Path

vinyl_map_path = Path(config.get('assets_path'), 'default', 'vinyl_map.json')

def get_default_image() -> Path:
        return Path(config.get('default_assets_path'), 'vinyl', 'vinyl_default_center.png')
    
def get_vinyl_noise() -> Path:
    return Path(config.get('default_assets_path'), 'vinyl_noise.mp3')
    
def get_result_path(username: str, id: int) -> Path:
    return Path(config.get('assets_path'), f'results/{username}_{id}/')

def get_cover_path(username: str, id: int) -> Path:
    return Path(config.get('assets_path'), f'covers/{username}_{id}/')

def get_vinyl_list() -> list[dict]:
    with open(vinyl_map_path, 'r') as f:
        return loads(f.read())

def get_vinyl_by_name(name: str):
    for v in get_vinyl_list():
            if v['name'] == name: return v