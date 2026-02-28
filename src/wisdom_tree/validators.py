"""Input validation utilities for Wisdom Tree."""

import re


class ValidationError(Exception):
    """Raised when input validation fails."""

    pass


class InputValidator:
    """Validates user input for various application features."""

    # YouTube URL regex pattern
    YOUTUBE_REGEX = re.compile(
        r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$', re.IGNORECASE
    )

    # Maximum reasonable URL length
    MAX_URL_LENGTH = 2048

    # Timer constraints (in minutes)
    MIN_TIMER_MINUTES = 1
    MAX_TIMER_MINUTES = 480  # 8 hours

    @staticmethod
    def validate_youtube_url(url: str) -> str:
        """Validate and normalize YouTube URL.

        Args:
            url: YouTube URL to validate

        Returns:
            Normalized URL (stripped of whitespace)

        Raises:
            ValidationError: If URL is invalid
        """
        if not url:
            raise ValidationError('URL cannot be empty')

        url = url.strip()

        if len(url) > InputValidator.MAX_URL_LENGTH:
            raise ValidationError(
                f'URL too long (max {InputValidator.MAX_URL_LENGTH} characters)'
            )

        if not InputValidator.YOUTUBE_REGEX.match(url):
            raise ValidationError(
                'Invalid YouTube URL format. URL must be from youtube.com or youtu.be'
            )

        return url

    @staticmethod
    def validate_timer_minutes(value: str) -> int:
        """Validate timer input as positive integer minutes.

        Args:
            value: User input string

        Returns:
            Validated timer duration in minutes

        Raises:
            ValidationError: If input is invalid
        """
        if not value or not value.strip():
            raise ValidationError('Timer duration cannot be empty')

        value = value.strip()

        try:
            minutes = int(value)
        except ValueError:
            raise ValidationError(
                f'Timer must be a whole number, got: "{value}"'
            ) from None

        if minutes < InputValidator.MIN_TIMER_MINUTES:
            raise ValidationError(
                f'Timer must be at least {InputValidator.MIN_TIMER_MINUTES} minute'
            )

        if minutes > InputValidator.MAX_TIMER_MINUTES:
            raise ValidationError(
                f'Timer cannot exceed {InputValidator.MAX_TIMER_MINUTES} minutes '
                f'({InputValidator.MAX_TIMER_MINUTES // 60} hours)'
            )

        return minutes

    @staticmethod
    def validate_volume(value: int) -> int:
        """Validate volume level.

        Args:
            value: Volume level (0-100)

        Returns:
            Validated volume level

        Raises:
            ValidationError: If volume is out of range
        """
        if not isinstance(value, int):
            raise ValidationError(f'Volume must be an integer, got: {type(value)}')

        if not 0 <= value <= 100:
            raise ValidationError(f'Volume must be between 0 and 100, got: {value}')

        return value

    @staticmethod
    def validate_age(age: int) -> int:
        """Validate tree age.

        Args:
            age: Tree age value

        Returns:
            Validated age

        Raises:
            ValidationError: If age is invalid
        """
        if not isinstance(age, int):
            raise ValidationError(f'Age must be an integer, got: {type(age)}')

        if age < 1:
            raise ValidationError(f'Age must be at least 1, got: {age}')

        # Reasonable upper limit (prevent integer overflow issues)
        if age > 1_000_000:
            raise ValidationError(f'Age exceeds maximum value: {age}')

        return age

    @staticmethod
    def sanitize_search_query(query: str, max_length: int = 200) -> str:
        """Sanitize a search query string.

        Args:
            query: Search query to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized query string

        Raises:
            ValidationError: If query is invalid
        """
        if not query or not query.strip():
            raise ValidationError('Search query cannot be empty')

        query = query.strip()

        if len(query) > max_length:
            raise ValidationError(
                f'Search query too long (max {max_length} characters)'
            )

        # Remove any null bytes or control characters
        query = ''.join(char for char in query if char.isprintable() or char.isspace())

        return query
