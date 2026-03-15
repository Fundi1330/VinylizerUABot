from movielite import ImageClip, AudioClip, VideoWriter, VideoClip
from PIL import Image
from io import BytesIO
from bot.config import config, logger
from .utils import get_default_image, get_vinyl_noise, get_cover_path, get_result_path, get_vinyl_by_name
from tinytag import TinyTag, ParseError
import os
import uuid

class Vinylizer:
    def __init__(self):
        pass

    def _rotate(self, k: int, speed: int, per: int):
        return -360 * speed * (k / per)
    
    def get_album_cover(self, user: dict, audio_tag: TinyTag, audio: str):
        cover_path = get_cover_path(user['username'], user['id'])

        if audio_tag.images.any:
            audio_image = audio_tag.images.any
            cover_img = Image.open(BytesIO(audio_image.data))
            cover_path = cover_path + f'{audio}.png'
            cover_img.save(cover_path, format='PNG')
        else: 
            cover_img = Image.open(get_default_image())
            cover_path = get_default_image()

        return cover_path

    def vinylize(
        self, 
        username: str, 
        user_id: int, 
        audio_path: str, 
        vinyl_name: str = 'default', 
        use_default_image: bool = False, 
        album_cover: str = None, 
        add_vinyl_noise: bool = False, 
        rpm: int = 10, 
        start: int = 0, 
        end: int = 60,
        size: tuple[float] = (500, 500)
    ) -> str:
        image_path = None
        user = {
            'username': username,
            'id': user_id
        }

        vinyl = get_vinyl_by_name(vinyl_name)
        
        if vinyl is None:
            vinyl = get_vinyl_by_name('default')

        try:
            audio_tag = TinyTag.get(audio_path)
        except ParseError:
            audio_tag = None
        except FileNotFoundError:
            logger.error(f'Audio file not found {audio_path}')

        if use_default_image and audio_tag is None:
            image_path = get_default_image()
        else:
            image_path = config.get('default_assets_path') + vinyl['image_without_center']
        
        if album_cover:
            cover_path = album_cover
        else:
            cover_path = self.get_album_cover(user, audio_tag, audio_path)
        

        os.makedirs(get_cover_path(user['username'], user['id']), exist_ok=True)

        video_clips: list[VideoClip] = []
        result_duration = 60
        audio = AudioClip(audio_path)
        if audio.duration < 60:
            result_duration = audio.duration
        end = result_duration + start - 1
        if end >= audio.duration:
            result_duration = audio.duration - start - 0.2
        audio = audio.subclip(start, end)
        audio.set_duration(result_duration)

        background = ImageClip(get_default_image())
        background.set_duration(result_duration)
        background.set_opacity(0)
        background.set_position((0, 0))
        background.set_size(*size)
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
        vinyl_clip.set_size(*size)
        video_clips.append(vinyl_clip)

        result_path = get_result_path(user['username'], user['id'])
        os.makedirs(result_path, exist_ok=True)
        result_name = uuid.uuid4()
        output_path = result_path + f'/{result_name}.mp4'
        for c in video_clips:
            c.set_rotation(lambda k: self._rotate(k, rpm, 60), expand=False) # Tie speed to minutes, and not the audio duration as it was before

        writer = VideoWriter(
            output_path=output_path,
            duration=result_duration,
            size=(size)
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

        if album_cover:
            os.remove(album_cover)
        os.remove(audio_path)

        return output_path