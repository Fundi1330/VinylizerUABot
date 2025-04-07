import logging
from json import loads
from os import getcwd

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

def load_config():
    with open('bot/config.json', 'r') as conf:
        config: dict = loads(conf.read())

    config['project_dir'] = getcwd() + '/bot'
    config['assets_path'] = config.get('project_dir') + '/assets/'
    config['default_assets_path'] = config.get('assets_path') + '/default/'

    return config

config = load_config()