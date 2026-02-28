"""Main Textual application for Wisdom Tree."""

import logging
import os
from dataclasses import dataclass

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Input, Label, ListItem, ListView, Static

from wisdom_tree.audio import MediaPlayer
from wisdom_tree.config import RES_FOLDER, AppConfig
from wisdom_tree.timer import PomodoroTimer
from wisdom_tree.tree import TreeManager
from wisdom_tree.tui.widgets import QuoteWidget, TimerWidget, TreeWidget
from wisdom_tree.utils import QuoteManager, StateManager
from wisdom_tree.validators import InputValidator, ValidationError

# Suppress VLC verbose output
os.environ['VLC_VERBOSE'] = '-1'

logger = logging.getLogger(__name__)


@dataclass
class Command:
    """Represents a command in the command palette."""

    name: str
    description: str
    action: str
    keybind: str = ''


class CommandPaletteScreen(ModalScreen):
    """Command palette screen for quick access to all actions."""

    BINDINGS = [
        Binding('escape', 'dismiss', 'Cancel', show=False),
        Binding('ctrl+p', 'dismiss', 'Close', show=False),
    ]

    def __init__(self, commands: list[Command]):
        """Initialize command palette with available commands."""
        super().__init__()
        self.commands = commands
        self.filtered_commands = commands.copy()

    def compose(self) -> ComposeResult:
        """Compose command palette content."""
        with Vertical(id='command-palette'):
            yield Label('Command Palette', id='palette-title')
            yield Input(
                placeholder='Type to search commands...',
                id='command-search',
            )
            with VerticalScroll(id='command-list-container'):
                yield ListView(id='command-list')

    def on_mount(self) -> None:
        """Focus the search input when mounted."""
        self.query_one('#command-search', Input).focus()
        self._populate_commands()

    def _populate_commands(self, filter_text: str = '') -> None:
        """Populate command list based on filter."""
        command_list = self.query_one('#command-list', ListView)
        command_list.clear()

        self.filtered_commands = [
            cmd
            for cmd in self.commands
            if filter_text.lower() in cmd.name.lower()
            or filter_text.lower() in cmd.description.lower()
        ]

        for cmd in self.filtered_commands:
            keybind_display = f'  [dim]{cmd.keybind}[/dim]' if cmd.keybind else ''
            item_text = f'[bold]{cmd.name}[/bold]{keybind_display}\n[dim]{cmd.description}[/dim]'
            list_item = ListItem(Static(item_text))
            command_list.append(list_item)

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == 'command-search':
            self._populate_commands(event.value)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in search - execute first command."""
        if self.filtered_commands:
            self.dismiss(self.filtered_commands[0].action)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle command selection from list."""
        index = event.list_view.index
        if index is not None and index < len(self.filtered_commands):
            self.dismiss(self.filtered_commands[index].action)


class YouTubeSearchScreen(ModalScreen):
    """Modal screen for YouTube search."""

    BINDINGS = [
        Binding('escape', 'dismiss', 'Cancel', show=False),
    ]

    def compose(self) -> ComposeResult:
        """Compose YouTube search modal content."""
        with Vertical(id='youtube-dialog'):
            yield Label('Enter YouTube URL or search query:', id='youtube-label')
            yield Input(placeholder='YouTube URL or search...', id='youtube-input')
            yield Label('Press ENTER to play, ESC to cancel', id='youtube-hint')

    def on_mount(self) -> None:
        """Focus the input when mounted."""
        self.query_one('#youtube-input', Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        query = event.value.strip()
        if query:
            # Validate if it's a URL
            is_url = False
            try:
                InputValidator.validate_youtube_url(query)
                is_url = True
            except ValidationError:
                # Not a URL, treat as search query
                is_url = False

            self.dismiss((query, is_url))
        else:
            self.dismiss(None)


class HelpScreen(ModalScreen):
    """Modal screen showing keyboard shortcuts."""

    BINDINGS = [
        Binding('escape,h,q', 'dismiss', 'Close', show=False),
    ]

    def compose(self) -> ComposeResult:
        """Compose help screen content."""
        help_text = """
[bold cyan]Keyboard Shortcuts[/bold cyan]

[bold yellow]Basic Actions[/bold yellow]
[yellow]q[/yellow]          Quit application
[yellow]space[/yellow]      Start/Stop Pomodoro timer
[yellow]r[/yellow]          Get new quote
[yellow]y[/yellow]          Play YouTube music
[yellow]ctrl+p[/yellow]     Command palette (all actions)

[bold yellow]Navigation (Vim-style)[/bold yellow]
[yellow]j / ↓[/yellow]      Navigate down
[yellow]k / ↑[/yellow]      Navigate up
[yellow]h / ←[/yellow]      Previous track
[yellow]l / →[/yellow]      Next track

[bold yellow]Volume Controls[/bold yellow]
[yellow][ / ][/yellow]      Media volume -/+
[yellow]{ / }[/yellow]      Sound effects -/+

[bold yellow]Media Controls[/bold yellow]
[yellow]m[/yellow]          Toggle music (pause/play)
[yellow]u[/yellow]          Toggle sound effects (mute/unmute)

[bold yellow]Help[/bold yellow]
[yellow]?[/yellow]          Show this help

[dim]Press ESC, h, or q to close[/dim]
        """
        with Vertical(id='help-dialog'):
            yield Static(help_text, id='help-content')

    def on_mount(self) -> None:
        """Focus the help screen when mounted."""
        self.query_one('#help-dialog').focus()


class WisdomTreeApp(App):
    """Wisdom Tree - A terminal-based concentration app with Textual UI."""

    CSS_PATH = 'styles.tcss'

    BINDINGS = [
        # Basic actions
        Binding('q', 'quit', 'Quit', show=False),
        Binding('space', 'toggle_timer', 'Start/Stop Timer', show=False),
        Binding('r', 'new_quote', 'New Quote', show=False),
        Binding('y', 'youtube', 'YouTube Music', show=False),
        # Volume controls
        Binding('[', 'volume_down', 'Volume -', show=False),
        Binding(']', 'volume_up', 'Volume +', show=False),
        Binding('{', 'effects_down', 'Effects -', show=False),
        Binding('}', 'effects_up', 'Effects +', show=False),
        # Media controls
        Binding('m', 'toggle_music', 'Toggle Music', show=False),
        Binding('u', 'toggle_sounds', 'Toggle Sounds', show=False),
        Binding('left,h', 'prev_track', 'Previous Track', show=False),
        Binding('right,l', 'next_track', 'Next Track', show=False),
        # Navigation (vim-style)
        Binding('k', 'navigate_up', 'Navigate Up', show=False),
        Binding('j', 'navigate_down', 'Navigate Down', show=False),
        Binding('up', 'navigate_up', 'Navigate Up', show=False),
        Binding('down', 'navigate_down', 'Navigate Down', show=False),
        # Help and command palette
        Binding('?', 'help', 'Help', show=False),
        Binding('ctrl+p', 'command_palette', 'Commands', show=True),
    ]

    def __init__(self, config: AppConfig | None = None):
        """Initialize Wisdom Tree app.

        Args:
            config: Application configuration (uses default if None)
        """
        super().__init__()
        self.config = config or AppConfig()

        # Initialize managers
        self.state_manager = StateManager(self.config.paths.state_file)
        initial_age = self.state_manager.load_tree_age()
        self.tree_manager = TreeManager(initial_age)
        self.quote_manager = QuoteManager()
        self.timer = PomodoroTimer()

        # Initialize media player
        music_files = list(RES_FOLDER.glob('*.ogg'))
        self.media_player = MediaPlayer(music_files)

        # Widget references (set in compose)
        self.tree_widget = None
        self.quote_widget = None
        self.timer_widget = None

    def compose(self) -> ComposeResult:
        """Compose the application layout.

        Returns:
            Widgets to display
        """
        with Container(id='main-container'):
            self.tree_widget = TreeWidget(self.tree_manager, id='tree')
            self.quote_widget = QuoteWidget(self.quote_manager, id='quote')
            self.timer_widget = TimerWidget(self.timer, id='timer')

            yield self.tree_widget
            yield self.quote_widget
            yield self.timer_widget

    def on_mount(self) -> None:
        """Called when app is mounted and ready.

        Sets up timers and starts the application.
        """
        # Set up quote rotation with tree growth
        self.set_interval(600.0, self._rotate_quote_and_grow)

        logger.info('Wisdom Tree app mounted and ready')

    def _rotate_quote_and_grow(self) -> None:
        """Rotate quote and grow tree (called every 10 minutes)."""
        if self.quote_widget:
            self.quote_widget.next_quote()
        if self.tree_widget:
            self.tree_widget.grow_tree()

    def action_toggle_timer(self) -> None:
        """Toggle Pomodoro timer start/stop."""
        import time

        if self.timer.istimer:
            # Stop timer
            self.timer.istimer = False
            self.notify('⏸️  Timer paused')
        else:
            # Start 25-minute focus session (preset 0: 25 min work, 5 min break)
            self.timer.istimer = True
            self.timer.worktime = self.config.timer.work_mins[0] * 60
            self.timer.breaktime = self.config.timer.break_mins[0] * 60
            self.timer.workendtime = int(time.time()) + self.timer.worktime
            self.notify('🍅 25-minute focus session started!')

            # Play start sound if not muted
            if not self.config.audio.sounds_muted:
                from wisdom_tree.audio import play_sound

                play_sound(str(self.config.paths.timer_start_sound))

    def action_new_quote(self) -> None:
        """Display a new random quote."""
        if self.quote_widget:
            self.quote_widget.next_quote()
            self.notify('💭 New wisdom unlocked')

    def action_youtube(self) -> None:
        """Open YouTube search modal and play music."""
        self.run_worker(self._youtube_workflow(), exclusive=True)

    async def _youtube_workflow(self) -> None:
        """Handle YouTube search and playback workflow in a worker."""
        result = await self.push_screen_wait(YouTubeSearchScreen())
        if result:
            query, is_url = result
            self.notify('🎵 Loading YouTube audio...')
            await self._play_youtube(query, is_url)

    async def _play_youtube(self, query: str, is_url: bool) -> None:
        """Play YouTube audio in background worker.

        Args:
            query: YouTube URL or search query
            is_url: True if query is a URL, False if search query
        """
        try:
            # Create a handler object to match the curses API expectations
            class NotificationHandler:
                def __init__(self, app):
                    self.app = app
                    # Create notifications object with notify method
                    self.notifications = self

                def notify(self, message: str, timeout: int = 5) -> None:
                    self.app.notify(message, timeout=timeout)

            handler = NotificationHandler(self)

            # Call the existing play_youtube method
            self.media_player.play_youtube(query, is_url, handler)

            if self.media_player.yt_title:
                self.notify(f'▶️  Playing: {self.media_player.yt_title}', timeout=10)
        except Exception as e:
            logger.error('YouTube playback error: %s', e)
            self.notify(f'❌ Error: {str(e)}', timeout=5)

    def action_volume_up(self) -> None:
        """Increase media volume."""
        self.config.audio.increase_volume(5)
        # TODO: MediaPlayer needs volume control methods
        self.notify(f'🔊 Volume: {self.config.audio.effect_volume}%')

    def action_volume_down(self) -> None:
        """Decrease media volume."""
        self.config.audio.decrease_volume(5)
        # TODO: MediaPlayer needs volume control methods
        self.notify(f'🔉 Volume: {self.config.audio.effect_volume}%')

    def action_effects_up(self) -> None:
        """Increase sound effects volume."""
        self.config.audio.increase_volume(5)
        self.notify(f'🔔 Effects: {self.config.audio.effect_volume}%')

    def action_effects_down(self) -> None:
        """Decrease sound effects volume."""
        self.config.audio.decrease_volume(5)
        self.notify(f'🔕 Effects: {self.config.audio.effect_volume}%')

    def action_toggle_music(self) -> None:
        """Toggle music playback."""
        # TODO: MediaPlayer needs is_playing and play/pause methods
        self.notify('🎵 Music toggle (not yet implemented)')

    def action_toggle_sounds(self) -> None:
        """Toggle sound effects on/off."""
        self.config.audio.toggle_mute()
        status = 'muted' if self.config.audio.sounds_muted else 'unmuted'
        self.notify(f'🔇 Sound effects {status}')

    def action_prev_track(self) -> None:
        """Play previous music track."""
        # TODO: MediaPlayer needs previous/next methods
        self.notify('⏮️  Previous track (not yet implemented)')

    def action_next_track(self) -> None:
        """Play next music track."""
        # TODO: MediaPlayer needs previous/next methods
        self.notify('⏭️  Next track (not yet implemented)')

    def action_help(self) -> None:
        """Show help modal with keyboard shortcuts."""
        self.push_screen(HelpScreen())

    def action_command_palette(self) -> None:
        """Show command palette for quick access to all actions."""

        def handle_command(action: str | None) -> None:
            """Handle selected command from palette."""
            if action:
                logger.info(f'Command palette: executing action {action}')
                # Execute the action
                try:
                    self.run_action(action)
                except Exception as e:
                    logger.error(f'Failed to execute action {action}: {e}')
                    self.notify(f'❌ Failed to execute: {action}')

        commands = [
            # Core actions
            Command('Quit', 'Exit the application', 'quit', 'q'),
            Command(
                'Start/Stop Timer', 'Toggle Pomodoro timer', 'toggle_timer', 'space'
            ),
            Command('New Quote', 'Get a new motivational quote', 'new_quote', 'r'),
            Command('YouTube Music', 'Play music from YouTube', 'youtube', 'y'),

            # Volume controls
            Command('Volume Up', 'Increase media volume', 'volume_up', ']'),
            Command('Volume Down', 'Decrease media volume', 'volume_down', '['),
            Command('Effects Up', 'Increase sound effects volume', 'effects_up', '}'),
            Command(
                'Effects Down', 'Decrease sound effects volume', 'effects_down', '{'
            ),

            # Media controls
            Command('Toggle Music', 'Pause/resume music playback', 'toggle_music', 'm'),
            Command('Toggle Sounds', 'Mute/unmute sound effects', 'toggle_sounds', 'u'),
            Command('Previous Track', 'Play previous track', 'prev_track', 'h/←'),
            Command('Next Track', 'Play next track', 'next_track', 'l/→'),

            # Theme selection
            Command('Theme: Textual Dark', 'Switch to dark theme', 'theme("textual-dark")'),
            Command('Theme: Textual Light', 'Switch to light theme', 'theme("textual-light")'),
            Command('Theme: Nord', 'Switch to Nord theme', 'theme("nord")'),
            Command('Theme: Monokai', 'Switch to Monokai theme', 'theme("monokai")'),
            Command('Theme: Dracula', 'Switch to Dracula theme', 'theme("dracula")'),
            Command('Theme: Tokyo Night', 'Switch to Tokyo Night theme', 'theme("tokyo-night")'),
            Command('Theme: Catppuccin', 'Switch to Catppuccin theme', 'theme("catppuccin")'),

            # Help
            Command('Help', 'Show keyboard shortcuts', 'help', '?'),
        ]

        self.push_screen(CommandPaletteScreen(commands), handle_command)

    def action_navigate_up(self) -> None:
        """Navigate up (vim-style k or arrow key)."""
        # Focus previous widget or scroll up
        self.screen.focus_previous()

    def action_navigate_down(self) -> None:
        """Navigate down (vim-style j or arrow key)."""
        # Focus next widget or scroll down
        self.screen.focus_next()

    def on_unmount(self) -> None:
        """Called when app is shutting down.

        Saves state and cleans up resources.
        """
        # Save tree age
        try:
            age = self.tree_manager.get_age()
            self.state_manager.save_tree_age(age)
            logger.info(f'Saved tree age: {age}')
        except Exception as e:
            logger.error(f'Failed to save tree age: {e}')

        # Pause media (MediaPlayer doesn't have stop method)
        if self.media_player and hasattr(self.media_player, 'pause'):
            try:
                self.media_player.pause()
            except Exception:
                pass  # Ignore errors during shutdown


def run() -> None:
    """Run the Wisdom Tree Textual application.

    This is the main entry point for the Textual UI.
    """
    app = WisdomTreeApp()
    app.run()


if __name__ == '__main__':
    run()
