from movielite import ImageClip, AudioClip, VideoWriter, VideoClip
from .utils import get_default_image, get_vinyl_noise, get_cover_path, get_result_path, get_vinyl_by_name, get_vinyl_folder
import os
import uuid
from pathlib import Path

class Vinylizer:
    def __init__(self):
        pass

    def _rotate(self, k: int, speed: int, per: int):
        return -360 * speed * (k / per)

    def vinylize(
        self, 
        username: str, 
        user_id: int, 
        audio_path: str, 
        vinyl_name: str = 'default', 
        cover_path: str | None = None, 
        with_noise: bool = False, 
        rpm: int = 10, 
        start: int = 0, 
        end: int = 60,
    ) -> str:
        vinyl_path = None
        user = {
            'username': username,
            'id': user_id
        }

        vinyl = get_vinyl_by_name(vinyl_name)
        
        if vinyl is None:
            vinyl = get_vinyl_by_name('default')

        size = (vinyl['result_size']['x'], vinyl['result_size']['y'])

        if cover_path:
            vinyl_path = str(Path(get_vinyl_folder(), vinyl['image_without_center']))
        else:
            vinyl_path = get_default_image()

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
        video_clips.append(background)

        if cover_path:
            cover = ImageClip(
                source=cover_path,
                duration=result_duration
            )
            aw, ah = cover.size
            cover_size = vinyl['cover_size']
            ax = cover_size['x']
            ay = cover_size['y']
            scale = min(ax, ay) / max(aw, ah)
            aw, ah = int(aw * scale), int(ah * scale)
            cover.set_size(aw, ah)
            cover_x = (w - aw) / 2
            cover_y = (h - ah) / 2
            cover.set_position((cover_x, cover_y))
            video_clips.append(cover)

        vinyl_clip = ImageClip(
            source=vinyl_path,
            duration=result_duration
        )
        vinyl_clip.set_position((0, 0))
        vinyl_clip.set_size(*size)
        video_clips.append(vinyl_clip)

        result_path = get_result_path(user['username'], user['id'])
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

        if with_noise:
            noise = AudioClip(
                path=get_vinyl_noise(), 
                duration=result_duration
            )
            writer.add_clip(noise)

        writer.write()

        if cover_path:
            os.remove(cover_path)
        os.remove(audio_path)

        return output_path