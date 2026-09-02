import logging
import urllib.request
from typing import Any

import vlc
from yt_dlp import YoutubeDL

from wisdom_tree.config import (
    ALARM_SOUND,
    EFFECT_VOLUME,
    SOUNDS_MUTED,
)


def is_internet_available() -> bool:
    try:
        urllib.request.urlopen('https://youtube.com', timeout=10)
        return True
    except Exception:
        return False


def play_sound(sound: str) -> None:
    if SOUNDS_MUTED and sound != ALARM_SOUND:
        return
    try:
        media = vlc.MediaPlayer(sound)
        media.audio_set_volume(EFFECT_VOLUME)
        media.play()
    except Exception as e:
        logging.error('Error playing sound: %s', e)


def toggle_sounds() -> None:
    global SOUNDS_MUTED
    SOUNDS_MUTED = not SOUNDS_MUTED
    logging.info('Sound toggled, muted: %s', SOUNDS_MUTED)


def extract_youtube_audio(song_input: str, is_url: bool) -> tuple[str, str]:
    query = song_input if is_url else f'ytsearch1:{song_input}'
    options = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }

    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(query, download=False)

    if info and info.get('entries') is not None:
        info = next((entry for entry in info['entries'] if entry), None)
    if not info or not info.get('url'):
        raise ValueError('No audio stream found for the video.')

    return info['url'], info.get('title') or song_input


def adjust_media_volume(tree_instance: Any, new_volume: int, maxx: int) -> None:
    volume = max(0, min(100, new_volume))
    tree_instance.media_player.media.audio_set_volume(volume)
    volume_str = f'{volume}%'
    padding = max(0, round(maxx * (volume / 100) - len(volume_str) - 2))
    tree_instance.notifications.notify(
        ' ' * padding + volume_str,
        invert=True,
    )


class MediaPlayer:
    def __init__(self, music_list):
        self.music_list = music_list
        self.music_list_num = 0
        self.media = vlc.MediaPlayer(str(self.music_list[self.music_list_num]))
        self.isloop = False
        self.yt_title = ''
        self.downloaddisplay = False
        self.youtubedisplay = False
        self.spinnerstate = 0
        self.isloading = False

    def play_youtube(self, song_input: str, is_url: bool, tree_instance: Any) -> None:
        self.downloaddisplay = True
        try:
            if not is_internet_available():
                tree_instance.notifications.notify('NO INTERNET CONNECTION', 5)
                return

            song, title = extract_youtube_audio(song_input, is_url)
            self.media = vlc.MediaPlayer(song)
            self.media.play()
            self.yt_title = title
            tree_instance.notifications.notify('Playing: ' + self.yt_title, 10)
        except Exception:
            logging.exception('Error getting YouTube audio for %s', song_input)
            tree_instance.notifications.notify(
                'ERROR GETTING AUDIO, PLEASE TRY AGAIN', 5
            )
        finally:
            self.downloaddisplay = False

    def handle_media_end(self):
        if (
            self.media.is_playing()
            and self.media.get_length() - self.media.get_time() < 1000
        ):
            if self.isloop:
                self.media.set_position(0)
            else:
                self.media.stop()
                self.media = vlc.MediaPlayer(self.music_list[self.music_list_num])
                self.media.play()

    def show_loading_spinner(self, stdscr, maxx):
        spinner = [
            '[    ]',
            '[=   ]',
            '[==  ]',
            '[=== ]',
            '[ ===]',
            '[  ==]',
            '[   =]',
            '[    ]',
            '[   =]',
            '[  ==]',
            '[ ===]',
            '[====]',
            '[=== ]',
            '[==  ]',
            '[=   ]',
        ]
        self.spinnerstate += 0.5
        if self.spinnerstate > len(spinner) - 1:
            self.spinnerstate = 0

        import curses

        curses.textpad.rectangle(stdscr, 0, 0, 2, maxx - 1)  # type: ignore
        stdscr.addstr(1, 1, 'GETTING AUDIO  ' + spinner[int(self.spinnerstate)])
