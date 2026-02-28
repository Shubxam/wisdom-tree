import json
import logging
import os
import random
import time
from pathlib import Path
from typing import TypedDict

from wisdom_tree.config import QUOTE_FILE

logger = logging.getLogger(__name__)


def get_user_config_directory() -> str:
    if os.name == 'nt':
        appdata = os.getenv('LOCALAPPDATA')
        if appdata:
            return appdata
        appdata = os.getenv('APPDATA')
        if appdata:
            return appdata
        return ''

    xdg_config_home = os.getenv('XDG_CONFIG_HOME')
    if xdg_config_home:
        return xdg_config_home
    return os.path.join(os.path.expanduser('~'), '.config')


class QuoteManager:
    def __init__(self):
        self.quotes_cache = self._load_quotes()

    def _load_quotes(self) -> list[str]:
        try:
            with open(QUOTE_FILE, encoding='utf8') as f:
                return f.read().splitlines()
        except Exception:
            return []

    def get_random_quote(self) -> str:
        if not self.quotes_cache:
            return 'Keep growing, keep learning.'
        return random.choice(self.quotes_cache)

    def reload_quotes(self) -> None:
        self.quotes_cache = self._load_quotes()


class TreeState(TypedDict):
    """Type definition for tree state data."""

    age: int
    last_saved: float
    version: str


class StateManager:
    """Manages persistent tree state using JSON serialization."""

    STATE_VERSION = '1.0'

    def __init__(self, state_file: Path):
        self.state_file = state_file.with_suffix('.json')
        self._migrate_from_pickle_if_needed()

    def save_tree_age(self, age: int) -> None:
        """Save tree state to JSON file.

        Args:
            age: Tree age (must be positive integer)

        Raises:
            ValueError: If age is invalid
            RuntimeError: If save operation fails
        """
        if not isinstance(age, int) or age < 1:
            raise ValueError(f'Age must be a positive integer, got: {age}')

        state: TreeState = {
            'age': age,
            'last_saved': time.time(),
            'version': self.STATE_VERSION,
        }

        try:
            # Write to temporary file first, then rename for atomicity
            temp_file = self.state_file.with_suffix('.json.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
            temp_file.replace(self.state_file)
        except OSError as e:
            logger.error(f'Failed to save tree state: {e}')
            raise RuntimeError(f'Failed to save state: {e}') from e

    def load_tree_age(self) -> int:
        """Load tree age from JSON file with validation.

        Returns:
            Tree age (defaults to 1 if file doesn't exist or is invalid)
        """
        if not self.state_file.exists():
            logger.debug('State file does not exist, starting with age 1')
            return 1

        try:
            with open(self.state_file, encoding='utf-8') as f:
                state = json.load(f)

            # Validate schema
            if not isinstance(state, dict):
                logger.warning('Invalid state format, resetting to age 1')
                return 1

            age = state.get('age', 1)
            if not isinstance(age, int) or age < 1:
                logger.warning(f'Invalid age value: {age}, resetting to 1')
                return 1

            logger.debug(f'Loaded tree age: {age}')
            return age

        except json.JSONDecodeError as e:
            logger.warning(f'Corrupt state file: {e}, resetting to age 1')
            return 1
        except OSError as e:
            logger.error(f'Error reading state file: {e}')
            return 1

    def _migrate_from_pickle_if_needed(self) -> None:
        """One-time migration from old pickle format to JSON.

        Looks for 'treedata' file (without extension) and migrates it.
        Creates a .pickle.bak backup of the original file.
        """
        old_pickle_file = self.state_file.with_suffix('')

        # If JSON already exists, no migration needed
        if self.state_file.exists():
            return

        # If old pickle file doesn't exist, nothing to migrate
        if not old_pickle_file.exists():
            return

        logger.info('Migrating from pickle format to JSON...')

        try:
            # Try to load the old pickle file
            import pickle

            with open(old_pickle_file, 'rb') as f:
                age = pickle.load(f)

            # Validate the loaded age
            if isinstance(age, int) and age >= 1:
                self.save_tree_age(age)
                # Backup the old file
                backup_file = old_pickle_file.with_suffix('.pickle.bak')
                old_pickle_file.rename(backup_file)
                logger.info(
                    f'Migration successful! Age: {age}, backup created at {backup_file}'
                )
            else:
                logger.warning(f'Invalid age in pickle file: {age}, starting fresh')
        except Exception as e:
            logger.warning(f'Failed to migrate pickle file: {e}, starting fresh')

    def file_exists(self) -> bool:
        """Check if state file exists."""
        return self.state_file.exists()


def get_random_line_from_file(file_path: Path) -> str:
    try:
        with open(file_path, encoding='utf8') as f:
            lines = f.read().splitlines()
        return random.choice(lines) if lines else ''
    except Exception:
        return ''


def ensure_directory_exists(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
