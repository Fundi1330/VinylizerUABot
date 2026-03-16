from bot.config import config, logger
from json import loads
from pathlib import Path
from tinytag import TinyTag, ParseError
from io import BytesIO
from PIL import Image

vinyl_map_path = Path(config.get('assets_path'), 'default', 'vinyl_map.json')

def get_vinyl_folder() -> str:
    return str(Path(config.get('default_assets_path'), 'vinyl'))

def get_preview_folder() -> str:
    return str(Path(config.get('default_assets_path'), 'preview'))

def get_default_image() -> str:
    return str(Path(get_vinyl_folder(), 'vinyl_default_center.png'))
    
def get_vinyl_noise() -> str:
    return str(Path(config.get('default_assets_path'), 'vinyl_noise.mp3'))
    
def get_result_path(username: str, id: int) -> str:
    return str(Path(config.get('assets_path'), f'results/{username}_{id}/'))

def get_user_audio_path(username: str, id: int) -> str:
    return str(Path(config.get('assets_path'), f'user_audios/{username}_{id}/'))

def get_cover_path(username: str, id: int) -> str:
    return str(Path(config.get('assets_path'), f'covers/{username}_{id}/'))

def get_vinyl_list() -> list[dict]:
    with open(vinyl_map_path, 'r') as f:
        return loads(f.read())

def get_vinyl_by_name(name: str) -> dict | None:
    for v in get_vinyl_list():
        if v['name'] == name: return v

def save_audio_cover(audio_path: str, save_path: str) -> str | None:
    '''Extracts cover tied to audio file and saves it on the disc if present'''
    try:
        audio_tag = TinyTag.get(audio_path, image=True)
    except ParseError:
        logger.error(f'Could not parse TinyTag {audio_path}')
        return None
    except FileNotFoundError:
        logger.error(f'Audio file not found {audio_path}')
        return None
    
    if not audio_tag:
        return None
    
    if audio_tag.images.any:
        try:
            audio_image = audio_tag.images.any
            cover_img = Image.open(BytesIO(audio_image.data))
            cover_img.save(save_path, format='PNG')
            logger.info(f'Successfully extracted cover to {save_path}')
            return save_path
        except Exception as e:
            logger.error(f'Failed to save cover: {e}')
            return None
    
    logger.debug(f'No cover found in {audio_path}')
    return None