"""Quote widget for displaying motivational quotes."""

from textual.widgets import Static

from wisdom_tree.utils import QuoteManager


class QuoteWidget(Static):
    """Display rotating motivational quotes."""

    def __init__(self, quote_manager: QuoteManager, **kwargs):
        """Initialize quote widget.

        Args:
            quote_manager: Quote manager instance
            **kwargs: Additional widget arguments
        """
        super().__init__(**kwargs)
        self.quote_manager = quote_manager
        self.current_quote = ''

    def on_mount(self) -> None:
        """Set up periodic quote updates when widget is mounted."""
        self.update_quote()
        # Rotate quote every 10 minutes (600 seconds)
        self.set_interval(600.0, self.update_quote)

    def update_quote(self) -> None:
        """Update to a new random quote."""
        self.current_quote = self.quote_manager.get_random_quote()
        self.update(f'"{self.current_quote}"')

    def get_quote(self) -> str:
        """Get the current quote text.

        Returns:
            Current quote string
        """
        return self.current_quote

    def next_quote(self) -> None:
        """Manually advance to next quote (triggered by user).

        This is useful for the 'r' key binding to refresh quotes.
        """
        self.update_quote()
