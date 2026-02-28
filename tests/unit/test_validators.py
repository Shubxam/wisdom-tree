"""Tests for input validators."""

import pytest

from wisdom_tree.validators import InputValidator, ValidationError


class TestYouTubeValidation:
    """Test suite for YouTube URL validation."""

    def test_valid_youtube_urls(self):
        """Test validation of valid YouTube URLs."""
        valid_urls = [
            'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'https://youtube.com/watch?v=dQw4w9WgXcQ',
            'http://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'https://youtu.be/dQw4w9WgXcQ',
            'http://youtu.be/dQw4w9WgXcQ',
            'www.youtube.com/watch?v=dQw4w9WgXcQ',
            'youtube.com/watch?v=dQw4w9WgXcQ',
            'youtu.be/dQw4w9WgXcQ',
        ]

        for url in valid_urls:
            result = InputValidator.validate_youtube_url(url)
            assert result == url.strip()

    def test_invalid_youtube_urls(self):
        """Test rejection of invalid YouTube URLs."""
        invalid_urls = [
            '',
            'not a url',
            'https://vimeo.com/123456',
            'https://www.google.com',
            'ftp://youtube.com/video',
        ]

        for url in invalid_urls:
            with pytest.raises(ValidationError):
                InputValidator.validate_youtube_url(url)

    def test_youtube_url_too_long(self):
        """Test rejection of extremely long URLs."""
        long_url = 'https://youtube.com/' + 'a' * 3000

        with pytest.raises(ValidationError, match='too long'):
            InputValidator.validate_youtube_url(long_url)

    def test_youtube_url_whitespace_stripped(self):
        """Test that whitespace is stripped from URLs."""
        url_with_whitespace = '  https://youtube.com/watch?v=test  '
        result = InputValidator.validate_youtube_url(url_with_whitespace)
        assert result == 'https://youtube.com/watch?v=test'


class TestTimerValidation:
    """Test suite for timer duration validation."""

    def test_valid_timer_values(self):
        """Test validation of valid timer durations."""
        valid_values = ['1', '25', '45', '90', '120', '480']

        for value in valid_values:
            result = InputValidator.validate_timer_minutes(value)
            assert result == int(value)

    def test_invalid_timer_values(self):
        """Test rejection of invalid timer durations."""
        invalid_values = [
            ('', 'cannot be empty'),
            ('   ', 'cannot be empty'),
            ('0', 'at least 1'),
            ('-5', 'at least 1'),
            ('abc', 'whole number'),
            ('12.5', 'whole number'),
            ('999', 'cannot exceed'),
        ]

        for value, expected_message in invalid_values:
            with pytest.raises(ValidationError, match=expected_message):
                InputValidator.validate_timer_minutes(value)

    def test_timer_whitespace_stripped(self):
        """Test that whitespace is stripped from timer input."""
        result = InputValidator.validate_timer_minutes('  25  ')
        assert result == 25


class TestVolumeValidation:
    """Test suite for volume level validation."""

    def test_valid_volume_levels(self):
        """Test validation of valid volume levels."""
        for volume in [0, 1, 50, 99, 100]:
            result = InputValidator.validate_volume(volume)
            assert result == volume

    def test_invalid_volume_type(self):
        """Test rejection of non-integer volumes."""
        with pytest.raises(ValidationError, match='must be an integer'):
            InputValidator.validate_volume(50.5)

        with pytest.raises(ValidationError, match='must be an integer'):
            InputValidator.validate_volume('50')

    def test_invalid_volume_range(self):
        """Test rejection of out-of-range volumes."""
        with pytest.raises(ValidationError, match='between 0 and 100'):
            InputValidator.validate_volume(-1)

        with pytest.raises(ValidationError, match='between 0 and 100'):
            InputValidator.validate_volume(101)


class TestAgeValidation:
    """Test suite for tree age validation."""

    def test_valid_ages(self):
        """Test validation of valid tree ages."""
        for age in [1, 10, 100, 1000, 100000]:
            result = InputValidator.validate_age(age)
            assert result == age

    def test_invalid_age_type(self):
        """Test rejection of non-integer ages."""
        with pytest.raises(ValidationError, match='must be an integer'):
            InputValidator.validate_age(42.5)

        with pytest.raises(ValidationError, match='must be an integer'):
            InputValidator.validate_age('42')

    def test_invalid_age_values(self):
        """Test rejection of invalid age values."""
        with pytest.raises(ValidationError, match='at least 1'):
            InputValidator.validate_age(0)

        with pytest.raises(ValidationError, match='at least 1'):
            InputValidator.validate_age(-10)

        with pytest.raises(ValidationError, match='exceeds maximum'):
            InputValidator.validate_age(2_000_000)


class TestSearchQuerySanitization:
    """Test suite for search query sanitization."""

    def test_valid_search_queries(self):
        """Test sanitization of valid queries."""
        valid_queries = [
            'lofi music',
            'concentration sounds',
            'focus playlist 2024',
        ]

        for query in valid_queries:
            result = InputValidator.sanitize_search_query(query)
            assert result == query

    def test_empty_query_rejected(self):
        """Test rejection of empty queries."""
        with pytest.raises(ValidationError, match='cannot be empty'):
            InputValidator.sanitize_search_query('')

        with pytest.raises(ValidationError, match='cannot be empty'):
            InputValidator.sanitize_search_query('   ')

    def test_query_too_long(self):
        """Test rejection of excessively long queries."""
        long_query = 'a' * 300

        with pytest.raises(ValidationError, match='too long'):
            InputValidator.sanitize_search_query(long_query)

    def test_query_whitespace_stripped(self):
        """Test that whitespace is stripped from queries."""
        result = InputValidator.sanitize_search_query('  test query  ')
        assert result == 'test query'

    def test_query_control_characters_removed(self):
        """Test that control characters are removed."""
        query_with_nulls = 'test\x00query\x01stuff'
        result = InputValidator.sanitize_search_query(query_with_nulls)
        assert '\x00' not in result
        assert '\x01' not in result
        assert 'testquerystuff' in result or 'test query stuff' in result
