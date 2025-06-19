import os
import time

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Static

from wisdom_tree.audio import MediaPlayer, play_sound
from wisdom_tree.config import RES_FOLDER, TIMER_START_SOUND
from wisdom_tree.timer import PomodoroTimer
from wisdom_tree.tree import TreeManager
from wisdom_tree.utils import QuoteManager, StateManager

os.environ["VLC_VERBOSE"] = "-1"


class TreeWidget(Static):
    """Widget to display the ASCII art tree."""

    def __init__(self, tree_manager: TreeManager, **kwargs):
        super().__init__(**kwargs)
        self.tree_manager = tree_manager
        self.update_timer = None

    def on_mount(self) -> None:
        """Set up periodic tree updates."""
        self.set_interval(1.0, self.update_tree)

    def update_tree(self) -> None:
        """Update the tree display."""
        art_content = self.get_current_art()
        age_text = f"\n\nAge: {self.tree_manager.get_age()}"
        self.update(art_content + age_text)

    def get_current_art(self) -> str:
        """Get the current tree art as text."""
        art_file = self.tree_manager.tree.get_art_file()
        try:
            with open(art_file, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "🌱 Tree is growing..."


class QuoteWidget(Static):
    """Widget to display rotating motivational quotes."""

    def __init__(self, quote_manager: QuoteManager, **kwargs):
        super().__init__(**kwargs)
        self.quote_manager = quote_manager

    def on_mount(self) -> None:
        """Set up periodic quote updates."""
        self.update_quote()
        self.set_interval(600.0, self.update_quote)  # Update every 10 minutes

    def update_quote(self) -> None:
        """Update the quote display."""
        quote = self.quote_manager.get_random_quote()
        self.update(f"💭 {quote}")


class TimerWidget(Static):
    """Widget to display timer information."""

    def __init__(self, timer: PomodoroTimer, **kwargs):
        super().__init__(**kwargs)
        self.timer = timer

    def on_mount(self) -> None:
        """Set up periodic timer updates."""
        self.set_interval(1.0, self.update_timer_display)

    def update_timer_display(self) -> None:
        """Update the timer display."""
        if self.timer.istimer:
            if self.timer.isbreak:
                remaining = self.timer.breakendtime - time.time()
                status = "🛌 Break Time"
            else:
                remaining = self.timer.workendtime - time.time()
                status = "🎯 Focus Time"

            if remaining > 0:
                mins, secs = divmod(int(remaining), 60)
                self.update(f"{status}: {mins:02d}:{secs:02d}")
            else:
                self.update("⏰ Timer Complete!")
        else:
            self.update("⏱️ No active timer")


class MenuWidget(Static):
    """Widget for navigation and menu options."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.menu_items = [
            "🍅 Pomodoro Timer",
            "🎵 Media Controls",
            "📝 Custom Quotes",
            "⚙️ Settings",
            "❌ Exit",
        ]
        self.selected_index = 0

    def on_mount(self) -> None:
        """Initialize menu display."""
        self.update_menu()

    def update_menu(self) -> None:
        """Update the menu display."""
        menu_text = "\n".join(
            f"{'> ' if i == self.selected_index else '  '}{item}"
            for i, item in enumerate(self.menu_items)
        )
        self.update(menu_text)

    def move_selection(self, direction: int) -> None:
        """Move menu selection up or down."""
        self.selected_index = (self.selected_index + direction) % len(self.menu_items)
        self.update_menu()


class NotificationWidget(Static):
    """Widget for displaying temporary notifications."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.notification_timer = None

    def show_notification(self, message: str, duration: float = 3.0) -> None:
        """Show a notification for a specified duration."""
        self.update(f"📢 {message}")
        self.add_class("notification-visible")

        if self.notification_timer:
            self.notification_timer.cancel()

        def hide_notification() -> None:
            self.update("")
            self.remove_class("notification-visible")

        self.set_timer(duration, hide_notification)


class WisdomTreeTextualApp(App):
    """Main Textual application for Wisdom Tree."""

    CSS = """
    Screen {
        background: $surface;
    }
    
    #tree-container {
        width: 60%;
        height: 100%;
        border: round $primary;
        padding: 1;
        background: $surface-lighten-1;
    }
    
    #tree-widget {
        text-align: center;
        content-align: center middle;
        color: $success;
    }
    
    #sidebar {
        width: 40%;
        height: 100%;
        background: $surface-darken-1;
    }
    
    #quote-widget {
        height: 25%;
        border: round $accent;
        padding: 1;
        text-align: center;
        content-align: center middle;
        background: $surface-lighten-1;
        color: $text;
        text-style: italic;
    }
    
    #timer-widget {
        height: 20%;
        border: round $warning;
        padding: 1;
        text-align: center;
        content-align: center middle;
        background: $surface-lighten-1;
        color: $warning;
        text-style: bold;
    }
    
    #menu-widget {
        height: 40%;
        border: round $secondary;
        padding: 1;
        background: $surface-lighten-1;
        color: $text;
    }
    
    #notification-widget {
        height: 15%;
        border: round $error;
        padding: 1;
        text-align: center;
        content-align: center middle;
        background: $surface;
    }
    
    .notification-visible {
        background: $warning;
        color: $text;
        text-style: bold;
        border: thick $warning;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("up", "menu_up", "Up"),
        ("down", "menu_down", "Down"),
        ("enter", "select", "Select"),
        ("space", "toggle_timer", "Toggle Timer"),
        ("m", "toggle_music", "Toggle Music"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Initialize managers and components
        self.state_manager = StateManager(RES_FOLDER / "treedata")
        initial_age = self.state_manager.load_tree_age()

        self.tree_manager = TreeManager(initial_age)
        self.timer = PomodoroTimer()
        self.quote_manager = QuoteManager()

        # Initialize media player
        music_list = list(RES_FOLDER.glob("*ogg"))
        self.media_player = MediaPlayer(music_list)

    def compose(self) -> ComposeResult:
        """Compose the app layout."""
        yield Header()

        with Horizontal():
            # Main tree display area
            with Vertical(id="tree-container"):
                yield TreeWidget(self.tree_manager, id="tree-widget")

            # Sidebar with controls
            with Vertical(id="sidebar"):
                yield QuoteWidget(self.quote_manager, id="quote-widget")
                yield TimerWidget(self.timer, id="timer-widget")
                yield MenuWidget(id="menu-widget")
                yield NotificationWidget(id="notification-widget")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the app when mounted."""
        self.title = "🌳 Wisdom Tree"
        self.sub_title = "Focus, Grow, Thrive"

        # Start background music
        if self.media_player.media:
            self.media_player.media.play()

        # Show welcome notification
        notification_widget = self.query_one("#notification-widget", NotificationWidget)
        notification_widget.show_notification("🌱 Welcome to Wisdom Tree!")

    def action_menu_up(self) -> None:
        """Move menu selection up."""
        menu_widget = self.query_one("#menu-widget", MenuWidget)
        menu_widget.move_selection(-1)

    def action_menu_down(self) -> None:
        """Move menu selection down."""
        menu_widget = self.query_one("#menu-widget", MenuWidget)
        menu_widget.move_selection(1)

    def action_select(self) -> None:
        """Handle menu selection."""
        menu_widget = self.query_one("#menu-widget", MenuWidget)
        notification_widget = self.query_one("#notification-widget", NotificationWidget)

        selected_item = menu_widget.menu_items[menu_widget.selected_index]

        if "Pomodoro Timer" in selected_item:
            self._handle_pomodoro_menu()
        elif "Media Controls" in selected_item:
            self._handle_media_menu()
        elif "Custom Quotes" in selected_item:
            notification_widget.show_notification(
                "📝 Custom quotes feature coming soon!"
            )
        elif "Settings" in selected_item:
            notification_widget.show_notification("⚙️ Settings feature coming soon!")
        elif "Exit" in selected_item:
            self.exit()

    def action_toggle_timer(self) -> None:
        """Toggle timer pause/resume."""
        if self.timer.istimer:
            self.timer.pause = not self.timer.pause
            notification_widget = self.query_one(
                "#notification-widget", NotificationWidget
            )
            status = "⏸️ Paused" if self.timer.pause else "▶️ Resumed"
            notification_widget.show_notification(f"Timer {status}")

    def action_toggle_music(self) -> None:
        """Toggle music playback."""
        if self.media_player.media:
            if self.media_player.media.is_playing():
                self.media_player.media.pause()
                status = "⏸️ Music Paused"
            else:
                self.media_player.media.play()
                status = "▶️ Music Playing"
        else:
            status = "❌ No media loaded"

        notification_widget = self.query_one("#notification-widget", NotificationWidget)
        notification_widget.show_notification(status)

    def _handle_pomodoro_menu(self) -> None:
        """Handle Pomodoro timer selection."""
        notification_widget = self.query_one("#notification-widget", NotificationWidget)

        if not self.timer.istimer:
            # Start a 25-minute Pomodoro session
            self.timer.start_timer(1, None, 80)  # Index 1 for 25-min timer
            play_sound(TIMER_START_SOUND)
            notification_widget.show_notification("🍅 25-minute Pomodoro started!")
        else:
            notification_widget.show_notification("⏱️ Timer already running!")

    def _handle_media_menu(self) -> None:
        """Handle media controls."""
        notification_widget = self.query_one("#notification-widget", NotificationWidget)
        notification_widget.show_notification("🎵 Use 'M' to toggle music")

    def on_unmount(self) -> None:
        """Clean up when app is unmounted."""
        # Save tree state
        self.state_manager.save_tree_age(self.tree_manager.get_age())

        # Stop media
        if self.media_player.media:
            self.media_player.media.stop()


def run_textual() -> None:
    """Entry point for the Textual version of Wisdom Tree."""
    app = WisdomTreeTextualApp()
    app.run()


if __name__ == "__main__":
    run_textual()
