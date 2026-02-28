"""Tree widget with weather effects for Textual TUI."""

import random
import time
from pathlib import Path

from textual.widgets import Static

from wisdom_tree.tree import TreeManager


class TreeWidget(Static):
    """Display ASCII art tree with animated weather effects."""

    # Weather effect configurations
    WEATHER_CONFIGS = {
        'rain': {'intensity': 30, 'speed': 30, 'char': '/', 'color': 'cyan'},
        'light_rain': {'intensity': 20, 'speed': 60, 'char': '`', 'color': 'cyan'},
        'heavy_rain': {'intensity': 40, 'speed': 20, 'char': '/', 'color': 'cyan'},
        'snow': {'intensity': 30, 'speed': 30, 'char': '.', 'color': 'white'},
        'windy': {'intensity': 20, 'speed': 30, 'char': '-', 'color': 'cyan'},
    }

    def __init__(self, tree_manager: TreeManager, **kwargs):
        """Initialize tree widget.

        Args:
            tree_manager: Tree state manager
            **kwargs: Additional widget arguments
        """
        super().__init__(**kwargs)
        self.tree_manager = tree_manager
        self.weather_season = self._get_daily_season()

    def _get_daily_season(self) -> str:
        """Get weather season based on daily seed for consistency.

        Returns:
            Weather season name
        """
        # Use day-based seed for consistent weather per day
        daily_seed = int(time.time() / (60 * 60 * 24))
        random.seed(daily_seed)
        season = random.choice(list(self.WEATHER_CONFIGS.keys()))
        random.seed()  # Reset to unpredictable
        return season

    def on_mount(self) -> None:
        """Set up periodic tree updates when widget is mounted."""
        self.set_interval(1.0, self.update_tree)

    def update_tree(self) -> None:
        """Update the tree display with current art."""
        art_content = self._get_current_art()
        age = self.tree_manager.get_age()
        self.update(f'{art_content}\n\n[bold green]Age:[/bold green] {age}')

    def _get_current_art(self) -> str:
        """Get current tree ASCII art based on age.

        Returns:
            Tree ASCII art as string
        """
        from pathlib import Path

        art_file_path = self.tree_manager.tree.get_art_file()
        try:
            return Path(art_file_path).read_text(encoding='utf-8')
        except FileNotFoundError:
            return '🌱 [italic]Tree is growing...[/italic]'

    def _generate_weather_effects(self) -> list[tuple[int, int, str, str]]:
        """Generate weather particle positions for current frame.

        Returns:
            List of (row, col, char, color) tuples
        """
        config = self.WEATHER_CONFIGS.get(
            self.weather_season, {'intensity': 0, 'speed': 30, 'char': '', 'color': ''}
        )

        if config['intensity'] == 0:
            return []

        # Time-based animation seed
        animation_seed = int(time.time() * 10 / config['speed'])
        random.seed(animation_seed)

        effects = []
        for _ in range(config['intensity']):
            row = random.randrange(2, 15)  # Tree area
            col = random.randrange(5, 60)  # Horizontal spread
            effects.append((row, col, config['char'], config['color']))

        random.seed()  # Reset
        return effects

    def _overlay_weather(
        self, tree_art: str, effects: list[tuple[int, int, str, str]]
    ) -> str:
        """Overlay weather effects onto tree art.

        Args:
            tree_art: Original tree ASCII art
            effects: List of weather effects to apply

        Returns:
            Tree art with weather effects overlaid
        """
        if not effects:
            return tree_art

        lines = tree_art.split('\n')

        # Group effects by row for proper insertion order
        effects_by_row: dict[int, list[tuple[int, str, str]]] = {}
        for row, col, char, color in effects:
            if row not in effects_by_row:
                effects_by_row[row] = []
            effects_by_row[row].append((col, char, color))

        # Process each row
        for row, row_effects in effects_by_row.items():
            # Bounds checking
            if row < 0 or row >= len(lines):
                continue

            line = lines[row]

            # Sort by column in reverse order to avoid index shifting
            row_effects.sort(key=lambda x: x[0], reverse=True)

            for col, char, color in row_effects:
                if col < 0:
                    continue

                # Extend line if needed
                if col >= len(line):
                    line += ' ' * (col - len(line) + 1)

                # Only overlay on empty spaces to preserve tree art
                if line[col] == ' ':
                    # Create colored character
                    colored_char = f'[{color}]{char}[/{color}]' if color else char

                    # Insert into line (processing right to left avoids index issues)
                    line = line[:col] + colored_char + line[col + 1 :]

            lines[row] = line

        return '\n'.join(lines)

    def grow_tree(self) -> None:
        """Trigger tree growth animation.

        Called when quote rotates (every 10 minutes).
        """
        self.tree_manager.tree.grow()
        self.update_tree()
