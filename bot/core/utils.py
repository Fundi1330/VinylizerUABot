from bot.config import config

def get_default_image():
        return config.get('default_assets_path') + 'vinyl_default.png'
    
def get_vinyl_noise():
    return config.get('default_assets_path') + 'vinyl_noise.mp3'
    
def get_result_path(username, id):
    return config.get('assets_path') + f'results/{username}_{id}/'

def get_cover_path(username, id):
    return config.get('assets_path') + f'covers/{username}_{id}/'