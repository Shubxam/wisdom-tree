"""Pytest configuration and fixtures for Wisdom Tree tests."""

import pytest

from wisdom_tree.config import AppConfig, AudioConfig, PathConfig


@pytest.fixture
def temp_state_file(tmp_path):
    """Temporary state file for testing.

    Args:
        tmp_path: pytest's tmp_path fixture

    Returns:
        Path to temporary state file
    """
    return tmp_path / 'test_state'


@pytest.fixture
def temp_dir(tmp_path):
    """Temporary directory for testing.

    Args:
        tmp_path: pytest's tmp_path fixture

    Returns:
        Path to temporary directory
    """
    return tmp_path


@pytest.fixture
def mock_paths(tmp_path):
    """Test path configuration with temporary paths.

    Args:
        tmp_path: pytest's tmp_path fixture

    Returns:
        PathConfig with temporary paths
    """
    # Create res directory for state files
    res_dir = tmp_path / 'res'
    res_dir.mkdir(exist_ok=True)

    return PathConfig(base_dir=tmp_path)


@pytest.fixture
def mock_config(tmp_path):
    """Test application configuration with temporary paths.

    Args:
        tmp_path: pytest's tmp_path fixture

    Returns:
        AppConfig with temporary paths
    """
    # Create res directory for state files
    res_dir = tmp_path / 'res'
    res_dir.mkdir(exist_ok=True)

    paths = PathConfig(base_dir=tmp_path)
    return AppConfig(paths=paths)


@pytest.fixture
def sample_quotes_file(tmp_path):
    """Create a sample quotes file for testing.

    Args:
        tmp_path: pytest's tmp_path fixture

    Returns:
        Path to quotes file
    """
    quotes_file = tmp_path / 'qts.txt'
    quotes_file.write_text(
        'First inspirational quote\n'
        'Second motivational quote\n'
        'Third wisdom quote\n'
        'Fourth profound thought\n',
        encoding='utf-8',
    )
    return quotes_file


@pytest.fixture
def empty_quotes_file(tmp_path):
    """Create an empty quotes file for testing.

    Args:
        tmp_path: pytest's tmp_path fixture

    Returns:
        Path to empty quotes file
    """
    quotes_file = tmp_path / 'qts.txt'
    quotes_file.write_text('', encoding='utf-8')
    return quotes_file


@pytest.fixture
def audio_config():
    """Default audio configuration for testing.

    Returns:
        AudioConfig instance
    """
    return AudioConfig()
