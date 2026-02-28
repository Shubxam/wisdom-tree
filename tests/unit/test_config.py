"""Tests for configuration classes."""

import pytest

from wisdom_tree.config import AppConfig, AudioConfig, PathConfig, TimerConfig


class TestPathConfig:
    """Test suite for PathConfig class."""

    def test_path_config_immutable(self):
        """Test that PathConfig is immutable (frozen)."""
        config = PathConfig()

        with pytest.raises(Exception):  # FrozenInstanceError
            config.base_dir = '/some/other/path'

    def test_res_folder_property(self, tmp_path):
        """Test res_folder property."""
        config = PathConfig(base_dir=tmp_path)
        assert config.res_folder == tmp_path / 'res'

    def test_quote_file_property(self, tmp_path):
        """Test quote_file property."""
        config = PathConfig(base_dir=tmp_path)
        assert config.quote_file == tmp_path / 'qts.txt'

    def test_sound_file_properties(self, tmp_path):
        """Test sound file path properties."""
        config = PathConfig(base_dir=tmp_path)

        assert config.timer_start_sound == tmp_path / 'res' / 'timerstart.wav'
        assert config.alarm_sound == tmp_path / 'res' / 'alarm.wav'
        assert config.growth_sound == tmp_path / 'res' / 'growth.waw'

    def test_state_file_property(self, tmp_path):
        """Test state_file property."""
        config = PathConfig(base_dir=tmp_path)
        assert config.state_file == tmp_path / 'res' / 'treedata'


class TestTimerConfig:
    """Test suite for TimerConfig class."""

    def test_timer_config_immutable(self):
        """Test that TimerConfig is immutable (frozen)."""
        config = TimerConfig()

        with pytest.raises(Exception):  # FrozenInstanceError
            config.work_mins = (30, 60)

    def test_default_work_durations(self):
        """Test default work durations."""
        config = TimerConfig()
        assert config.work_mins == (25, 45, 50, 90)

    def test_default_break_durations(self):
        """Test default break durations."""
        config = TimerConfig()
        assert config.break_mins == (5, 15, 10, 20)

    def test_work_seconds_conversion(self):
        """Test work durations converted to seconds."""
        config = TimerConfig()
        assert config.work_seconds == (1500, 2700, 3000, 5400)

    def test_break_seconds_conversion(self):
        """Test break durations converted to seconds."""
        config = TimerConfig()
        assert config.break_seconds == (300, 900, 600, 1200)

    def test_custom_durations(self):
        """Test custom timer durations."""
        config = TimerConfig(work_mins=(10, 20), break_mins=(2, 4))

        assert config.work_mins == (10, 20)
        assert config.break_mins == (2, 4)
        assert config.work_seconds == (600, 1200)
        assert config.break_seconds == (120, 240)


class TestAudioConfig:
    """Test suite for AudioConfig class."""

    def test_audio_config_mutable(self):
        """Test that AudioConfig is mutable."""
        config = AudioConfig()

        # Should be able to modify
        config.sounds_muted = True
        assert config.sounds_muted is True

        config.effect_volume = 50
        assert config.effect_volume == 50

    def test_default_values(self):
        """Test default audio values."""
        config = AudioConfig()
        assert config.sounds_muted is False
        assert config.effect_volume == 100

    def test_volume_validation_in_init(self):
        """Test volume validation during initialization."""
        # Valid volumes
        config = AudioConfig(effect_volume=0)
        assert config.effect_volume == 0

        config = AudioConfig(effect_volume=100)
        assert config.effect_volume == 100

        # Invalid volumes
        with pytest.raises(ValueError, match='between 0 and 100'):
            AudioConfig(effect_volume=-1)

        with pytest.raises(ValueError, match='between 0 and 100'):
            AudioConfig(effect_volume=101)

    def test_increase_volume(self):
        """Test volume increase method."""
        config = AudioConfig(effect_volume=50)

        config.increase_volume(10)
        assert config.effect_volume == 60

        config.increase_volume()  # Default is 1
        assert config.effect_volume == 61

    def test_increase_volume_caps_at_100(self):
        """Test that volume increase caps at 100."""
        config = AudioConfig(effect_volume=95)

        config.increase_volume(10)
        assert config.effect_volume == 100  # Capped, not 105

    def test_decrease_volume(self):
        """Test volume decrease method."""
        config = AudioConfig(effect_volume=50)

        config.decrease_volume(10)
        assert config.effect_volume == 40

        config.decrease_volume()  # Default is 1
        assert config.effect_volume == 39

    def test_decrease_volume_floors_at_0(self):
        """Test that volume decrease floors at 0."""
        config = AudioConfig(effect_volume=5)

        config.decrease_volume(10)
        assert config.effect_volume == 0  # Floored, not -5

    def test_toggle_mute(self):
        """Test mute toggle method."""
        config = AudioConfig(sounds_muted=False)

        config.toggle_mute()
        assert config.sounds_muted is True

        config.toggle_mute()
        assert config.sounds_muted is False


class TestAppConfig:
    """Test suite for AppConfig class."""

    def test_app_config_default_initialization(self):
        """Test AppConfig initializes with defaults."""
        config = AppConfig()

        assert isinstance(config.paths, PathConfig)
        assert isinstance(config.timer, TimerConfig)
        assert isinstance(config.audio, AudioConfig)

    def test_app_config_with_custom_components(self, tmp_path):
        """Test AppConfig with custom components."""
        paths = PathConfig(base_dir=tmp_path)
        timer = TimerConfig(work_mins=(30,), break_mins=(5,))
        audio = AudioConfig(effect_volume=75)

        config = AppConfig(paths=paths, timer=timer, audio=audio)

        assert config.paths.base_dir == tmp_path
        assert config.timer.work_mins == (30,)
        assert config.audio.effect_volume == 75

    def test_app_config_paths_accessible(self, tmp_path):
        """Test that paths are accessible through AppConfig."""
        paths = PathConfig(base_dir=tmp_path)
        config = AppConfig(paths=paths)

        assert config.paths.res_folder == tmp_path / 'res'
        assert config.paths.quote_file == tmp_path / 'qts.txt'

    def test_app_config_timer_accessible(self):
        """Test that timer config is accessible through AppConfig."""
        config = AppConfig()

        assert config.timer.work_mins == (25, 45, 50, 90)
        assert config.timer.work_seconds[0] == 1500  # 25 * 60

    def test_app_config_audio_modifiable(self):
        """Test that audio config can be modified through AppConfig."""
        config = AppConfig()

        config.audio.increase_volume(5)
        # Should be capped at 100 (was already at 100)
        assert config.audio.effect_volume == 100

        config.audio.effect_volume = 50
        config.audio.increase_volume(10)
        assert config.audio.effect_volume == 60

        config.audio.toggle_mute()
        assert config.audio.sounds_muted is True
