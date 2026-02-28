# Navigation & Command Palette

This document explains the navigation improvements and command palette feature added to Wisdom Tree's Textual UI.

## Command Palette (Ctrl+P)

Press `Ctrl+P` to open the command palette - a searchable list of all available actions.

### Features:
- **Fuzzy search**: Type to filter commands by name or description
- **Keyboard navigation**: Use `↑`/`↓` or `k`/`j` to navigate
- **Quick execute**: Press Enter to execute the highlighted command
- **Mouse support**: Click any command to execute it
- **Keybind hints**: Shows the keyboard shortcut for each action

### Available Commands:
- Quit
- Start/Stop Timer
- New Quote
- YouTube Music
- Volume Up/Down
- Effects Up/Down
- Toggle Music
- Toggle Sounds
- Previous/Next Track
- Help

## Vim-Style Navigation

The app now supports vim-style keyboard navigation inspired by the original ncurses implementation:

### Navigation Keys:
- `j` or `↓` - Navigate down
- `k` or `↑` - Navigate up
- `h` or `←` - Previous track (or back in menus)
- `l` or `→` - Next track (or forward in menus)

### Comparison to Original ncurses Navigation:

**Original ncurses (main.py:250-318)**:
- Used arrow keys and vim keys for menu navigation
- `h/k/j/l` moved through menu hierarchy
- Left/Esc closed submenus
- Right/Enter opened submenus or selected items
- Menu had auto-fade after 5 seconds of inactivity

**Textual Implementation**:
- Vim keys (`hjkl`) + arrow keys for consistent navigation
- `j`/`k` navigate up/down through focusable elements
- `h`/`l` control media (previous/next track)
- Command palette (`Ctrl+P`) replaces the menu system
- More modern UX with searchable commands

## Implementation Details

### Files Modified:
1. **src/wisdom_tree/tui/app.py**:
   - Added `Command` dataclass for command metadata
   - Added `CommandPaletteScreen` modal with search and list view
   - Added `action_command_palette()` to show the palette
   - Added `action_navigate_up()` and `action_navigate_down()` for vim navigation
   - Updated bindings to include vim keys and Ctrl+P
   - Updated help screen with new keybindings

2. **src/wisdom_tree/tui/styles.tcss**:
   - Added CSS styles for command palette modal
   - Styled search input, command list, and list items
   - Added hover effects for better UX

### Technical Notes:
- The command palette uses Textual's `ListView` for the command list
- Real-time filtering updates the list as you type
- Commands map to action methods via `self.run_action()`
- Navigation actions use Textual's built-in focus system

## Usage Examples

### Using Command Palette:
1. Press `Ctrl+P`
2. Type "youtube" to filter
3. Press Enter or click to execute

### Using Vim Navigation:
1. Press `j` to move focus down
2. Press `k` to move focus up
3. Press `h` for previous track
4. Press `l` for next track

### Quick Actions:
- `space` - Start/stop timer
- `r` - New quote
- `y` - YouTube search
- `m` - Toggle music
- `?` - Show help
