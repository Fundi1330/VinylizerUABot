from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, CompositeAudioClip
from PIL import Image
from io import BytesIO
from telegram import User
from bot.config import config, logger
from .utils import get_default_image, get_vinyl_noise, get_cover_path, get_result_path
from stagger import read_tag, id3
from os import makedirs

rotation_speed = None

class Vynilizer:

    def __init__(self, user: User, music: str, use_default_image: bool = False):
        self.user = user
        self.music = music
        self.use_default_image = use_default_image
     
    def rotation(self, k):
        return -360 * self.rotation_speed * (k / self.duration)
    
    def get_album_cover(self, music_tag):
        cover_path = get_cover_path(self.user.username, self.user.id)

        if id3.APIC in music_tag.keys():
            music_data = music_tag[id3.APIC][0].data
            cover_img = Image.open(BytesIO(music_data))
            cover_path = cover_path + f'{self.music}.png'
            cover_img.save(cover_path, format='PNG')
        else: 
            cover_img = Image.open(get_default_image())
            cover_path = get_default_image()

        return cover_path

    async def vynilize(self, album_cover: str = None, add_vinyl_noise: bool = False, rpm: int = 10, start: int = 0, end: int = 59):
        # load image
        image_path = None
        user = self.user

        music_path = config.get('assets_path') + f'user_audios/{user.username}_{user.id}/{self.music}'

        music_tag = read_tag(music_path)


        if self.use_default_image:
            image_path = get_default_image()
        else:
            image_path = config.get('default_assets_path') + 'vinyl_no_center.png'
        
        
        if album_cover:
            cover_path = album_cover
        else:
            cover_path = self.get_album_cover(music_tag)
        

        makedirs(get_cover_path(self.user.username, self.user.id), exist_ok=True)

        video_clips = []
        result_duration = 59
        audio = AudioFileClip(music_path)
        if audio.duration < 59:
            result_duration = audio.duration
        end = result_duration + start - 1
        if end >= audio.duration:
            result_duration = audio.duration - start - 0.2
        
        self.duration = result_duration

        audio = audio.subclipped(start, end).with_duration(result_duration)

        background = ImageClip(get_default_image()).with_opacity(0).with_duration(result_duration)
        video_clips.append(background)

        cover = ImageClip(cover_path).with_duration(result_duration)
        if cover_path == get_default_image():
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


        vinyl = ImageClip(image_path).with_duration(result_duration).with_position(('center', 'center'))
        video_clips.append(vinyl)


        music_path = config.get('assets_path') + f'user_audios/{user.username}_{user.id}/{self.music}'




        result_path = get_result_path(self.user.username, self.user.id)
        makedirs(result_path, exist_ok=True)

        result = CompositeVideoClip(video_clips).with_duration(result_duration).with_audio(audio)

        if add_vinyl_noise:
            noise = AudioFileClip(get_vinyl_noise()).with_duration(result_duration)
            audio_with_noise = CompositeAudioClip([audio, noise])
            result = result.with_audio(audio_with_noise)

        self.rotation_speed = rpm
        result = result.rotated(lambda k: self.rotation(k))
        result = result.write_videofile(result_path + f'{self.music}.mp4', fps=24)

        return result_path + f'{self.music}.mp4'