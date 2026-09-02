import logging

import wisdom_tree.audio as audio


class FakeYoutubeDL:
    instances = []
    response = {}

    def __init__(self, options):
        self.options = options
        self.queries = []
        type(self).instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def extract_info(self, query, download):
        self.queries.append((query, download))
        return type(self).response


class FakeNotifications:
    def __init__(self):
        self.messages = []

    def notify(self, message, duration=2, invert=False):
        self.messages.append((message, duration, invert))


class FakeTree:
    def __init__(self):
        self.notifications = FakeNotifications()


def test_extracts_audio_from_direct_url(monkeypatch):
    FakeYoutubeDL.instances.clear()
    FakeYoutubeDL.response = {
        'title': 'Focus track',
        'url': 'https://audio.example/focus.webm',
    }
    monkeypatch.setattr(audio, 'YoutubeDL', FakeYoutubeDL)

    url, title = audio.extract_youtube_audio(
        'https://www.youtube.com/watch?v=abc123', is_url=True
    )

    assert (url, title) == ('https://audio.example/focus.webm', 'Focus track')
    ydl = FakeYoutubeDL.instances[-1]
    assert ydl.queries == [('https://www.youtube.com/watch?v=abc123', False)]
    assert ydl.options['format'] == 'bestaudio/best'
    assert ydl.options['noplaylist'] is True
    assert ydl.options['skip_download'] is True


def test_searches_for_first_matching_audio_result(monkeypatch):
    FakeYoutubeDL.instances.clear()
    FakeYoutubeDL.response = {
        'entries': [
            None,
            {
                'title': 'First result',
                'url': 'https://audio.example/result.webm',
            },
        ]
    }
    monkeypatch.setattr(audio, 'YoutubeDL', FakeYoutubeDL)

    url, title = audio.extract_youtube_audio('focus music', is_url=False)

    assert (url, title) == ('https://audio.example/result.webm', 'First result')
    assert FakeYoutubeDL.instances[-1].queries == [('ytsearch1:focus music', False)]


def test_playback_uses_extracted_url_and_title(monkeypatch):
    class FakeVlcMedia:
        instances = []

        def __init__(self, url):
            self.url = url
            self.played = False
            type(self).instances.append(self)

        def play(self):
            self.played = True

    player = object.__new__(audio.MediaPlayer)
    player.downloaddisplay = False
    tree = FakeTree()
    monkeypatch.setattr(audio, 'is_internet_available', lambda: True)
    monkeypatch.setattr(
        audio,
        'extract_youtube_audio',
        lambda *_: ('https://audio.example/focus.webm', 'Focus track'),
    )
    monkeypatch.setattr(audio.vlc, 'MediaPlayer', FakeVlcMedia)

    player.play_youtube('focus music', is_url=False, tree_instance=tree)

    assert player.media.url == 'https://audio.example/focus.webm'
    assert player.media.played is True
    assert player.yt_title == 'Focus track'
    assert player.downloaddisplay is False
    assert tree.notifications.messages == [('Playing: Focus track', 10, False)]


def test_playback_failure_clears_loading_state_and_logs(monkeypatch, caplog):
    player = object.__new__(audio.MediaPlayer)
    player.downloaddisplay = False
    tree = FakeTree()
    error = RuntimeError('extractor failed')
    monkeypatch.setattr(audio, 'is_internet_available', lambda: True)
    monkeypatch.setattr(
        audio, 'extract_youtube_audio', lambda *_: (_ for _ in ()).throw(error)
    )

    with caplog.at_level(logging.ERROR):
        player.play_youtube('focus music', is_url=False, tree_instance=tree)

    assert player.downloaddisplay is False
    assert tree.notifications.messages == [
        ('ERROR GETTING AUDIO, PLEASE TRY AGAIN', 5, False)
    ]
    assert 'extractor failed' in caplog.text
