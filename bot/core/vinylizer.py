from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, CompositeAudioClip
from PIL import Image
from io import BytesIO
from bot.config import config, logger
from .utils import get_default_image, get_vinyl_noise, get_cover_path, get_result_path
from stagger import read_tag, id3
from stagger.errors import NoTagError
from os import makedirs

class Vinylizer:
    def __init__(self):
        pass

    def __rotation(self, k):
        return -360 * self.rotation_speed * (k / self.duration)
    
    def get_album_cover(self, music_tag, music):
        cover_path = get_cover_path(self.user.get('username'), self.user.get('id'))

        if music_tag is not None and id3.APIC in music_tag.keys():
            music_data = music_tag[id3.APIC][0].data
            cover_img = Image.open(BytesIO(music_data))
            cover_path = cover_path + f'{music}.png'
            cover_img.save(cover_path, format='PNG')
        else: 
            cover_img = Image.open(get_default_image())
            cover_path = get_default_image()

        return cover_path

    def vinylize(self, username: str, user_id: int, music: str, use_default_image: bool = False, album_cover: str = None, add_vinyl_noise: bool = False, rpm: int = 10, start: int = 0, end: int = 60) -> str:
        image_path = None
        music
        self.user = {
            'username': username,
            'id': user_id
        }

        user = self.user

        music_path = config.get('assets_path') + f'user_audios/{user.get('username')}_{user.get('id')}/{music}'

        try:
            music_tag = read_tag(music_path)
        except NoTagError:
            music_tag = None

        if use_default_image and music_tag is None:
            image_path = get_default_image()
        else:
            image_path = config.get('default_assets_path') + 'vinyl_no_center.png'
        
        
        if album_cover:
            cover_path = album_cover
        else:
            cover_path = self.get_album_cover(music_tag, music)
        

        makedirs(get_cover_path(self.user.get('username'), self.user.get('id')), exist_ok=True)

        video_clips = []
        result_duration = 60
        audio = AudioFileClip(music_path)
        if audio.duration < 60:
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


        music_path = config.get('assets_path') + f'user_audios/{user.get('username')}_{user.get('id')}/{music}'




        result_path = get_result_path(self.user.get('username'), self.user.get('id'))
        makedirs(result_path, exist_ok=True)

        result = CompositeVideoClip(video_clips).with_duration(result_duration).with_audio(audio)

        if add_vinyl_noise:
            noise = AudioFileClip(get_vinyl_noise()).with_duration(result_duration)
            audio_with_noise = CompositeAudioClip([audio, noise])
            result = result.with_audio(audio_with_noise)

        self.rotation_speed = rpm
        result = result.rotated(lambda k: self.__rotation(k))
        result = result.write_videofile(result_path + f'{music}.mp4', fps=24)

        return result_path + f'{music}.mp4'