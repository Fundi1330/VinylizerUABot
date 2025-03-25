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
    logger.info(getcwd())
    with open('bot/config.json', 'r') as conf:
        config = loads(conf.read())

    config['project_dir'] = getcwd()

    return config

config = load_config()