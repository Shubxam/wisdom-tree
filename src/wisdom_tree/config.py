"""Configuration management for Wisdom Tree application."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class PathConfig:
    """Immutable path configuration."""

    base_dir: Path = field(default_factory=lambda: Path(__file__).parent)

    @property
    def res_folder(self) -> Path:
        """Resource folder path."""
        return self.base_dir / 'res'

    @property
    def quote_folder(self) -> Path:
        """Quote folder path."""
        return self.base_dir

    @property
    def quote_file(self) -> Path:
        """Main quotes file path."""
        return self.quote_folder / 'qts.txt'

    @property
    def timer_start_sound(self) -> Path:
        """Timer start sound file path."""
        return self.res_folder / 'timerstart.wav'

    @property
    def alarm_sound(self) -> Path:
        """Alarm sound file path."""
        return self.res_folder / 'alarm.wav'

    @property
    def growth_sound(self) -> Path:
        """Growth sound file path."""
        return self.res_folder / 'growth.waw'

    @property
    def state_file(self) -> Path:
        """Tree state file path."""
        return self.res_folder / 'treedata'


@dataclass(frozen=True)
class TimerConfig:
    """Immutable timer configuration."""

    work_mins: tuple[int, ...] = (25, 45, 50, 90)
    break_mins: tuple[int, ...] = (5, 15, 10, 20)

    @property
    def work_seconds(self) -> tuple[int, ...]:
        """Work durations in seconds."""
        return tuple(m * 60 for m in self.work_mins)

    @property
    def break_seconds(self) -> tuple[int, ...]:
        """Break durations in seconds."""
        return tuple(m * 60 for m in self.break_mins)


@dataclass
class AudioConfig:
    """Mutable audio configuration for runtime state."""

    sounds_muted: bool = False
    effect_volume: int = 100

    def __post_init__(self):
        """Validate audio settings."""
        if not isinstance(self.effect_volume, int):
            raise TypeError('effect_volume must be an integer')
        if not 0 <= self.effect_volume <= 100:
            raise ValueError('effect_volume must be between 0 and 100')

    def increase_volume(self, amount: int = 1) -> None:
        """Increase effect volume."""
        self.effect_volume = min(100, self.effect_volume + amount)

    def decrease_volume(self, amount: int = 1) -> None:
        """Decrease effect volume."""
        self.effect_volume = max(0, self.effect_volume - amount)

    def toggle_mute(self) -> None:
        """Toggle sound mute state."""
        self.sounds_muted = not self.sounds_muted


@dataclass
class AppConfig:
    """Application-wide configuration."""

    paths: PathConfig = field(default_factory=PathConfig)
    timer: TimerConfig = field(default_factory=TimerConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)


# Backwards compatibility: expose commonly used paths as module-level constants
# These are READ-ONLY and should not be mutated
_DEFAULT_PATHS = PathConfig()
BASE_DIR = _DEFAULT_PATHS.base_dir
RES_FOLDER = _DEFAULT_PATHS.res_folder
QUOTE_FOLDER = _DEFAULT_PATHS.quote_folder
QUOTE_FILE = _DEFAULT_PATHS.quote_file
QUOTE_FILE_NAME = 'qts.txt'

_DEFAULT_TIMER = TimerConfig()
TIMER_WORK_MINS = _DEFAULT_TIMER.work_mins
TIMER_BREAK_MINS = _DEFAULT_TIMER.break_mins
TIMER_WORK = _DEFAULT_TIMER.work_seconds
TIMER_BREAK = _DEFAULT_TIMER.break_seconds

# Sound file paths (READ-ONLY)
TIMER_START_SOUND = str(_DEFAULT_PATHS.timer_start_sound)
ALARM_SOUND = str(_DEFAULT_PATHS.alarm_sound)
GROWTH_SOUND = str(_DEFAULT_PATHS.growth_sound)

# Deprecated: These should not be used as globals
# They are kept for backwards compatibility but will be removed in future versions
SOUNDS_MUTED = False
EFFECT_VOLUME = 100
