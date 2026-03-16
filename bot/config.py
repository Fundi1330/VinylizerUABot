import logging
from json import loads
from os import getcwd
from dataclasses import dataclass
from pathlib import Path

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


@dataclass
class PlanConfig:
    length: int
    price: int


@dataclass
class Config:
    admins: list[int]
    supported_audio_types: list[str]
    database_path: str
    payload: str
    max_video_duration: int
    max_free_video_duration: int
    plans: list[PlanConfig]
    project_dir: str = None
    assets_path: str = None
    default_assets_path: str = None

    def __post_init__(self):
        if self.project_dir is None:
            self.project_dir = str(Path(getcwd()) / 'bot')
        if self.assets_path is None:
            self.assets_path = str(Path(self.project_dir) / 'assets')
        if self.default_assets_path is None:
            self.default_assets_path = str(Path(self.assets_path) / 'default')


def load_config() -> Config:
    with open('bot/config.json', 'r') as conf:
        config_data: dict = loads(conf.read())
    
    plans = [PlanConfig(**plan) for plan in config_data.get('plans', [])]
    
    return Config(
        admins=config_data.get('admins', []),
        supported_audio_types=config_data.get('supported_audio_types', []),
        database_path=config_data.get('database_path', ''),
        payload=config_data.get('payload', ''),
        max_video_duration=config_data.get('max_video_duration', 0),
        max_free_video_duration=config_data.get('max_free_video_duration', 0),
        plans=plans,
    )


config = load_config()