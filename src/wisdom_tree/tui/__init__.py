"""Textual TUI package for Wisdom Tree."""

__all__ = ['WisdomTreeApp', 'run']

# Lazy import to avoid circular issues when running as __main__
def __getattr__(name):
    if name == 'WisdomTreeApp':
        from wisdom_tree.tui.app import WisdomTreeApp
        return WisdomTreeApp
    if name == 'run':
        from wisdom_tree.tui.app import run
        return run
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
