from movielite import ImageClip, AudioClip, VideoWriter, VideoClip
from PIL import Image
from io import BytesIO
from bot.config import config, logger
from .utils import get_default_image, get_vinyl_noise, get_cover_path, get_result_path, get_vinyl_by_name
from tinytag import TinyTag, ParseError
from os import makedirs

class Vinylizer:
    def __init__(self):
        pass

    def __rotation(self, k: int):
        return -360 * self.rotation_speed * (k / self.duration)
    
    def get_album_cover(self, music_tag: TinyTag, music: str):
        cover_path = get_cover_path(self.user.get('username'), self.user.get('id'))

        if music_tag.images.any:
            music_image = music_tag.images.any
            cover_img = Image.open(BytesIO(music_image.data))
            cover_path = cover_path + f'{music}.png'
            cover_img.save(cover_path, format='PNG')
        else: 
            cover_img = Image.open(get_default_image())
            cover_path = get_default_image()

        return cover_path

    def vinylize(
        self, 
        username: str, 
        user_id: int, 
        music: str, 
        vinyl_name: str = 'default', 
        use_default_image: bool = False, 
        album_cover: str = None, 
        add_vinyl_noise: bool = False, 
        rpm: int = 10, 
        start: int = 0, 
        end: int = 60
    ) -> str:
        image_path = None
        self.user = {
            'username': username,
            'id': user_id
        }

        user = self.user

        vinyl = get_vinyl_by_name(vinyl_name)
        
        if vinyl is None:
            vinyl = get_vinyl_by_name('default')

        music_path = config.get('assets_path') + f"user_audios/{user.get('username')}_{user.get('id')}/{music}"

        try:
            music_tag = TinyTag.get(music_path)
        except ParseError:
            music_tag = None

        if use_default_image and music_tag is None:
            image_path = get_default_image()
        else:
            image_path = config.get('default_assets_path') + vinyl['image_without_center']
        
        if album_cover:
            cover_path = album_cover
        else:
            cover_path = self.get_album_cover(music_tag, music)
        

        makedirs(get_cover_path(self.user.get('username'), self.user.get('id')), exist_ok=True)

        video_clips: list[VideoClip] = []
        result_duration = 60
        audio = AudioClip(music_path)
        if audio.duration < 60:
            result_duration = audio.duration
        end = result_duration + start - 1
        if end >= audio.duration:
            result_duration = audio.duration - start - 0.2
        
        self.duration = result_duration

        audio.set_start(start)
        audio.set_end(end)
        audio.set_duration(result_duration)

        background = ImageClip(get_default_image())
        background.set_duration(result_duration)
        background.set_opacity(0)
        background.set_position((0, 0))
        background.set_size(500, 500)
        h, w = background.size
        cx, cy = h / 2, w / 2
        video_clips.append(background)

        cover = ImageClip(
            source=cover_path,
            duration=result_duration
        )

        if cover_path == get_default_image():
            image_path = cover_path
        else:
            aw, ah = cover.size
            album_size = vinyl['album_size']
            ax = album_size['x']
            ay = album_size['y']
            scale = min(ax, ay) / max(aw, ah)
            cover.set_scale(scale)
            aw, ah = cover.size[0] * scale, cover.size[1] * scale
            cover_x = cx - aw / 2
            cover_y = cy - ah / 2
            cover.set_position((cover_x, cover_y))
            video_clips.append(cover)


        vinyl_clip = ImageClip(
            source=image_path,
            duration=result_duration
        )
        vinyl_clip.set_position((0, 0))
        vinyl_clip.set_size(500, 500)
        video_clips.append(vinyl_clip)

        music_path = config.get('assets_path') + f"user_audios/{user.get('username')}_{user.get('id')}/{music}"

        result_path = get_result_path(self.user.get('username'), self.user.get('id'))
        makedirs(result_path, exist_ok=True)
        output_path = result_path + f'{music}.mp4'
        print(rpm)
        self.rotation_speed = rpm
        for c in video_clips:
            c.set_rotation(lambda k: self.__rotation(k), expand=False)

        writer = VideoWriter(
            output_path=output_path,
            duration=result_duration,
            size=(500, 500)
        )
        writer.add_clips(video_clips)
        writer.add_clip(audio)

        if add_vinyl_noise:
            noise = AudioClip(
                path=get_vinyl_noise(), 
                duration=result_duration
            )
            writer.add_clip(noise)

        writer.write()


        return output_path