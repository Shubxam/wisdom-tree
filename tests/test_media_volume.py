from wisdom_tree.main import key_events


class FakeMedia:
    def __init__(self, volume: int = 50):
        self.volume = volume

    def audio_get_volume(self) -> int:
        return self.volume

    def audio_set_volume(self, volume: int) -> None:
        self.volume = volume


class FakeMediaPlayer:
    def __init__(self):
        self.media = FakeMedia()


class FakeNotifications:
    def __init__(self):
        self.calls = []

    def notify(self, message: str, duration: int = 2, invert: bool = False) -> None:
        self.calls.append((message, duration, invert))


class FakeApp:
    def __init__(self):
        self.media_player = FakeMediaPlayer()
        self.notifications = FakeNotifications()


class FakeScreen:
    def __init__(self, key: int):
        self.key = key

    def getch(self) -> int:
        return self.key


def test_volume_down_updates_current_media_and_notifies() -> None:
    app = FakeApp()

    key_events(FakeScreen(ord('[')), app, 80)

    assert app.media_player.media.volume == 49
    message, duration, invert = app.notifications.calls[-1]
    assert message.endswith('49%')
    assert duration == 2
    assert invert is True
