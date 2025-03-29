from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, ColorClip
from moviepy.video.fx import MaskColor
from PIL import Image
from io import BytesIO
from telegram import User
from bot.config import config, logger
from stagger import read_tag, id3
from os import makedirs

class Vynilizer:
    def __init__(self, user: User, music: str, use_default_image: bool = False):
        self.user = user
        self.music = music
        self.use_default_image = use_default_image

    def get_default_image(self):
        return config.get('assets_path') + 'images/vinyl_default.png'
    
    def get_result_path(self):
        return config.get('assets_path') + f'results/{self.user.username}_{self.user.id}/'

    def get_cover_path(self):
        return config.get('assets_path') + f'covers/{self.user.username}_{self.user.id}/'
    
    def rotation(t, k):
        return -10 * k

    async def vynilize(self):
        # load image
        image_path = None
        user = self.user

        music_path = config.get('assets_path') + f'user_audios/{user.username}_{user.id}/{self.music}'

        music_cover = read_tag(music_path)


        if self.use_default_image:
            image_path = self.get_default_image()
        else:
            image_path = config.get('assets_path') + 'images/vinyl_no_center.png'
        
        
        
        cover_img = None
        cover_path = self.get_cover_path()

        if id3.APIC in music_cover.keys():
            music_data = music_cover[id3.APIC][0].data
            cover_img = Image.open(BytesIO(music_data))
            cover_path = cover_path + f'{self.music}.png'
            cover_img.save(cover_path, format='PNG')
        else: 
            cover_img = Image.open(self.get_default_image())
            cover_path = self.get_default_image()

        makedirs(self.get_cover_path(), exist_ok=True)

        video_clips = []
        background = ImageClip(self.get_default_image()).with_opacity(0).with_duration(59)
        video_clips.append(background)

        cover = ImageClip(cover_path).with_duration(59)
        if cover_path == self.get_default_image():
            image_path = cover_path
        else:
            w, h = cover.size

            if w > h:
                x1, x2 = (w - h) // 2, (w + h) // 2 
                y1, y2 = 0, h 
            else:
                x1, x2 = 0, w
                y1, y2 = (h - w) // 2, (h + w) // 2 

            cover = cover.cropped(x1=x1, y1=y1, x2=x2, y2=y2).resized((150, 150)).with_position(('center', 'center')) 
            video_clips.append(cover)


        vinyl = ImageClip(image_path).with_duration(59).with_position(('center', 'center'))
        video_clips.append(vinyl)


        music_path = config.get('assets_path') + f'user_audios/{user.username}_{user.id}/{self.music}'

        audio = AudioFileClip(music_path).with_duration(59)


        result_path = self.get_result_path()
        makedirs(result_path, exist_ok=True)

        

        result = CompositeVideoClip(video_clips).with_duration(59).with_audio(audio)
        result = result.rotated(self.rotation)
        result = result.write_videofile(result_path + f'{self.music}.mp4', fps=24)

        return result_path + f'{self.music}.mp4'