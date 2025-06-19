import os
import time
import random

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Static, Input
from textual.screen import ModalScreen
import threading

from wisdom_tree.audio import MediaPlayer
from wisdom_tree.config import RES_FOLDER
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
        self.weather_season = self._get_daily_season()

    def _get_daily_season(self) -> str:
        """Get weather season based on daily seed."""
        random.seed(int(time.time() / (60 * 60 * 24)))
        season = random.choice(["rain", "heavy_rain", "light_rain", "snow", "windy"])
        random.seed()
        return season

    def on_mount(self) -> None:
        """Set up periodic tree updates."""
        self.set_interval(1.0, self.update_tree)

    def update_tree(self) -> None:
        """Update the tree display."""
        art_content = self.get_current_art()
        weather_overlay = self._generate_weather_overlay()
        age_text = f"\n\nAge: {self.tree_manager.get_age()}"
        
        # Combine tree art with weather effects
        combined_content = self._overlay_weather(art_content, weather_overlay)
        self.update(combined_content + age_text)

    def get_current_art(self) -> str:
        """Get the current tree art as text."""
        art_file = self.tree_manager.tree.get_art_file()
        try:
            with open(art_file, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "🌱 Tree is growing..."

    def _generate_weather_overlay(self) -> dict:
        """Generate weather effects based on current season."""
        current_time = time.time()
        
        weather_params = {
            "rain": {"intensity": 30, "speed": 30, "char": "/", "color": "cyan"},
            "light_rain": {"intensity": 20, "speed": 60, "char": "`", "color": "cyan"},
            "heavy_rain": {"intensity": 40, "speed": 20, "char": "/", "color": "cyan"},
            "snow": {"intensity": 30, "speed": 30, "char": ".", "color": "white"},
            "windy": {"intensity": 20, "speed": 30, "char": "-", "color": "cyan"}
        }
        
        params = weather_params.get(self.weather_season, {"intensity": 0, "speed": 30, "char": "", "color": "white"})
        
        # Use time-based seeding for animation
        random.seed(int(current_time / int(params["speed"])))
        
        effects = []
        for _ in range(int(params["intensity"])):
            # Generate weather particle positions
            row = random.randrange(2, 15)  # Spread across more of the tree area
            col = random.randrange(5, 60)  # Wider horizontal spread
            effects.append({
                "row": row,
                "col": col,
                "char": params["char"],
                "color": params["color"]
            })
        
        random.seed()  # Reset seed
        return {"effects": effects}

    def _overlay_weather(self, tree_art: str, weather_data: dict) -> str:
        """Overlay weather effects onto tree art."""
        if not weather_data.get("effects"):
            return tree_art
            
        lines = tree_art.split('\n')
        
        # Apply weather effects
        for effect in weather_data["effects"]:
            row, col = effect["row"], effect["col"]
            char = effect["char"]
            
            # Check bounds
            if 0 <= row < len(lines) and 0 <= col < len(lines[row]):
                # Convert line to list for modification
                line_chars = list(lines[row])
                
                # Only overlay on spaces to avoid overwriting tree art
                if col < len(line_chars) and line_chars[col] == ' ':
                    if effect["color"] == "cyan":
                        line_chars[col] = f"[cyan]{char}[/cyan]"
                    elif effect["color"] == "white":
                        line_chars[col] = f"[white]{char}[/white]"
                    else:
                        line_chars[col] = char
                    
                    lines[row] = ''.join(line_chars)
                # Also try to add weather at the end of shorter lines
                elif col >= len(line_chars):
                    # Extend line with spaces then add weather
                    padding = ' ' * (col - len(line_chars))
                    if effect["color"] == "cyan":
                        weather_char = f"[cyan]{char}[/cyan]"
                    elif effect["color"] == "white":
                        weather_char = f"[white]{char}[/white]"
                    else:
                        weather_char = char
                    lines[row] = lines[row] + padding + weather_char
        
        return '\n'.join(lines)


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
                status = "Break"
            else:
                remaining = self.timer.workendtime - time.time()
                status = "Focus"

            if remaining > 0:
                mins, secs = divmod(int(remaining), 60)
                self.update(f"{status}: {mins:02d}:{secs:02d}")
            else:
                self.update("Complete!")
                self.timer.istimer = False
        else:
            self.update("Press SPACE to start 25min focus")


class HelpScreen(ModalScreen):
    """Modal screen to show keyboard shortcuts."""
    
    BINDINGS = [
        ("escape", "dismiss", "Close"),
        ("q", "dismiss", "Close"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the help screen."""
        help_text = """
┌─ Keyboard Shortcuts ─┐
│                      │
│  SPACE  Start/Stop   │
│  M      Music Toggle │
│  Y      YouTube      │
│  R      New Quote    │
│  ?      Help         │
│  Q      Quit         │
│                      │
│  ESC    Close Help   │
└──────────────────────┘
        """
        yield Static(help_text, id="help-content")
    
    def action_dismiss(self) -> None:
        """Close the help screen."""
        self.app.pop_screen()


class YouTubeScreen(ModalScreen):
    """Modal screen for YouTube search/URL input."""
    
    BINDINGS = [
        ("escape", "dismiss", "Close"),
        ("ctrl+c", "dismiss", "Close"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the YouTube input screen."""
        yield Static("🎵 Enter YouTube URL or search term:", id="youtube-prompt")
        yield Input(placeholder="Search or paste URL...", id="youtube-input")
        yield Static("ESC to cancel", id="youtube-help")
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle YouTube input submission."""
        query = event.value.strip()
        if query:
            self.dismiss(query)
        else:
            self.dismiss(None)
    
    def action_dismiss(self) -> None:
        """Close the YouTube screen."""
        self.dismiss(None)


class WisdomTreeTextualApp(App):
    """Main Textual application for Wisdom Tree."""

    CSS = """
    Screen {
        background: black;
    }
    
    #tree-widget {
        height: 75%;
        text-align: center;
        content-align: center middle;
        color: green;
    }
    
    #quote-widget {
        height: 20%;
        text-align: center;
        content-align: center middle;
        color: white;
        text-style: italic;
    }
    
    #timer-widget {
        height: 5%;
        text-align: center;
        content-align: center middle;
        color: yellow;
    }
    
    HelpScreen {
        align: center middle;
    }
    
    #help-content {
        width: 30;
        height: 12;
        background: $surface;
        color: $text;
        border: thick $primary;
        text-align: center;
        content-align: center middle;
        padding: 1;
    }
    
    YouTubeScreen {
        align: center middle;
    }
    
    #youtube-prompt {
        width: 50;
        height: 1;
        text-align: center;
        color: $text;
        margin: 1;
    }
    
    #youtube-input {
        width: 50;
        margin: 1;
    }
    
    #youtube-help {
        width: 50;
        height: 1;
        text-align: center;
        color: $secondary;
        margin: 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("space", "toggle_timer", "Start/Stop Timer"),
        ("m", "toggle_music", "Toggle Music"),
        ("y", "show_youtube", "YouTube"),
        ("r", "refresh_quote", "New Quote"),
        ("question_mark", "show_help", "Help"),
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
        music_list = list(RES_FOLDER.glob("*.ogg"))
        self.media_player = MediaPlayer(music_list)

    def compose(self) -> ComposeResult:
        """Compose the app layout."""
        with Vertical():
            yield TreeWidget(self.tree_manager, id="tree-widget")
            yield QuoteWidget(self.quote_manager, id="quote-widget")
            yield TimerWidget(self.timer, id="timer-widget")

    def on_mount(self) -> None:
        """Initialize the app when mounted."""
        self.title = "Wisdom Tree"
        
        # Start background music if available
        if self.media_player.media:
            self.media_player.media.play()


    def action_toggle_timer(self) -> None:
        """Start or stop the timer."""
        if not self.timer.istimer:
            # Start 25-minute focus session
            self.timer.start_timer(1, None, 80)  # 25 minutes
        else:
            # Stop the timer
            self.timer.istimer = False
            self.timer.pause = False
    
    def action_show_help(self) -> None:
        """Show the help screen."""
        self.push_screen(HelpScreen())
    
    def action_toggle_music(self) -> None:
        """Toggle music playback."""
        if self.media_player.media:
            if self.media_player.media.is_playing():
                self.media_player.media.pause()
            else:
                self.media_player.media.play()
    
    def action_show_youtube(self) -> None:
        """Show YouTube input screen."""
        def handle_youtube_result(query):
            if query:
                # Start YouTube playback in background thread
                threading.Thread(
                    target=self._play_youtube_audio,
                    args=(query,),
                    daemon=True
                ).start()
        
        self.push_screen(YouTubeScreen(), handle_youtube_result)
    
    def _play_youtube_audio(self, query: str) -> None:
        """Play audio from YouTube in background thread."""
        try:
            # Determine if input is a URL or search query
            import re
            youtube_url_pattern = r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$'
            is_url = bool(re.match(youtube_url_pattern, query))
            
            # Use the media player's YouTube functionality
            self.media_player.play_youtube(query, is_url, self.tree_manager.tree)
        except Exception:
            # Handle errors silently for now
            pass
    
    def action_refresh_quote(self) -> None:
        """Refresh the quote display with a new random quote."""
        quote_widget = self.query_one("#quote-widget", QuoteWidget)
        quote_widget.update_quote()


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
