
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Wisdom Tree is a terminal-based concentration app inspired by Plants vs. Zombies' wisdom tree. It displays motivational quotes as a tree grows during focus sessions, includes Pomodoro timers, and plays ambient music to enhance concentration. The app uses `curses` for the terminal interface and `vlc` for audio playback.

## Development Commands

- **Install for development**: `uv sync` or `pip install -e .`
- **Run the application**: `python -m wisdom_tree` (after package install) or `python src/wisdom_tree/main.py`
- **Build package**: `uv build` (creates wheel and source distribution)
- **Install from build**: `pip install dist/wisdom_tree-*.whl`
- **Linting**: `ruff check src/` (available in dev dependencies)
- **Code formatting**: `ruff format src/` (available in dev dependencies)
- **Run installed CLI**: `wisdom-tree` (after installation)

## Architecture

### Core Components

- **src/wisdom_tree/main.py**: Main application entry point containing the `tree` class and curses-based UI logic
- **src/wisdom_tree/config.py**: Configuration settings for timers, file paths, and sound settings  
- **src/wisdom_tree/edit_quotes.py**: Quote processing utility with Scanner class for text formatting
- **src/wisdom_tree/res/**: Resource directory containing:
  - Audio files (.ogg, .wav) for music and sound effects
  - ASCII art files (p1.txt - p9.txt) representing different tree growth stages
  - quotes file (qts.txt) with motivational content
- **pyproject.toml**: Modern Python packaging with hatchling build system and uv dependency management

### Key Classes and Functions

- **tree class** (src/wisdom_tree/main.py:262): Core application state and UI management
  - Handles menu navigation, timer functionality, media playback
  - Manages tree growth stages and visual display
  - Contains YouTube music integration via pytubefix
- **key_events()** (src/wisdom_tree/main.py:149): Input handling for navigation and controls
- **Scanner class** (src/wisdom_tree/edit_quotes.py): Quote processing with finite state machine for punctuation handling
- **Configuration constants** (src/wisdom_tree/config.py): Timer presets, file paths, sound settings

### Application Flow

1. Load tree age from saved state (`src/wisdom_tree/res/treedata` pickle file)
2. Initialize curses interface with color pairs and input settings  
3. Main loop displays tree art, quotes, menus, and handles user input
4. Menu system: Main menu → Sub-menus (Pomodoro timers, Media options)
5. Timer functionality with work/break cycles and audio notifications
6. Quote rotation every 10 minutes with tree growth

### Media and Audio

- Uses python-vlc for media playback
- Supports local .ogg files from src/wisdom_tree/res/ directory
- YouTube integration for streaming music (requires internet)
- Volume controls for both media and sound effects
- Preset concentration music option

### Dependencies

- **python-vlc**: Media playback
- **pytubefix**: YouTube audio streaming  
- **requests**: HTTP requests for YouTube
- **curses**: Terminal UI (built-in)
- **VLC media player**: Required system dependency

## Build System and Packaging

- **Build Backend**: Hatchling with VCS versioning (`hatch-vcs` plugin)
- **Package Manager**: Uses `uv` for fast dependency resolution and environment management
- **Entry Point**: Console script `wisdom-tree` configured in `[project.scripts]`
- **Package Structure**: Source layout with `src/wisdom_tree/` directory structure
- **Version Strategy**: Automatic versioning from git tags and commits
- **Resource Handling**: Package data includes ASCII art, audio files, and quotes via `[tool.hatch.build]` configuration

## Important Implementation Details

- Quote caching in memory for performance (QUOTES_CACHE)
- Tree age persistence via pickle serialization
- Custom user quotes supported in config directory
- Menu fade-out effect based on last activity timestamp
- Seasonal visual effects (rain, snow, wind) with randomization
- Platform-specific config directory detection (Windows/Mac/Linux)
- State machine pattern for menu navigation and timer management
- Cross-platform terminal compatibility with graceful color fallbacks