"""Tests for Textual UI widgets."""

import pytest
from textual.pilot import Pilot

from wisdom_tree.config import AppConfig
from wisdom_tree.timer import PomodoroTimer
from wisdom_tree.tree import TreeManager
from wisdom_tree.tui.app import WisdomTreeApp
from wisdom_tree.tui.widgets import QuoteWidget, TimerWidget, TreeWidget
from wisdom_tree.utils import QuoteManager


class TestTreeWidget:
    """Test suite for TreeWidget."""

    @pytest.mark.asyncio
    async def test_tree_widget_initializes(self, tmp_path):
        """Test tree widget initializes correctly."""
        tree_manager = TreeManager(1)
        widget = TreeWidget(tree_manager, id='test-tree')

        assert widget.tree_manager == tree_manager
        assert widget.weather_season in TreeWidget.WEATHER_CONFIGS

    @pytest.mark.asyncio
    async def test_tree_widget_updates(self, tmp_path):
        """Test tree widget updates display."""
        tree_manager = TreeManager(5)
        widget = TreeWidget(tree_manager, id='test-tree')

        # Should not crash when updating
        widget.update_tree()

    @pytest.mark.asyncio
    async def test_tree_widget_grows(self, tmp_path):
        """Test tree growth updates age."""
        tree_manager = TreeManager(1)
        widget = TreeWidget(tree_manager, id='test-tree')

        initial_age = tree_manager.get_age()
        widget.grow_tree()

        # Age should have increased
        assert tree_manager.get_age() > initial_age

    @pytest.mark.asyncio
    async def test_weather_effects_generation(self, tmp_path):
        """Test weather effects are generated."""
        tree_manager = TreeManager(1)
        widget = TreeWidget(tree_manager, id='test-tree')

        effects = widget._generate_weather_effects()

        # Should return a list (may be empty depending on weather)
        assert isinstance(effects, list)

        # Each effect should be a tuple of (row, col, char, color)
        for effect in effects:
            assert isinstance(effect, tuple)
            assert len(effect) == 4


class TestQuoteWidget:
    """Test suite for QuoteWidget."""

    @pytest.mark.asyncio
    async def test_quote_widget_initializes(self, sample_quotes_file):
        """Test quote widget initializes correctly."""
        quote_manager = QuoteManager()
        widget = QuoteWidget(quote_manager, id='test-quote')

        assert widget.quote_manager == quote_manager

    @pytest.mark.asyncio
    async def test_quote_widget_updates(self, sample_quotes_file):
        """Test quote widget updates display."""
        quote_manager = QuoteManager()
        widget = QuoteWidget(quote_manager, id='test-quote')

        widget.update_quote()

        # Should have a quote
        assert len(widget.current_quote) > 0

    @pytest.mark.asyncio
    async def test_quote_widget_next_quote(self, sample_quotes_file):
        """Test advancing to next quote."""
        quote_manager = QuoteManager()
        widget = QuoteWidget(quote_manager, id='test-quote')

        widget.update_quote()
        first_quote = widget.current_quote

        # Get next quote (might be the same due to randomness, but method should work)
        widget.next_quote()
        assert len(widget.current_quote) > 0

    @pytest.mark.asyncio
    async def test_get_quote_returns_current(self, sample_quotes_file):
        """Test get_quote returns current quote."""
        quote_manager = QuoteManager()
        widget = QuoteWidget(quote_manager, id='test-quote')

        widget.update_quote()
        assert widget.get_quote() == widget.current_quote


class TestTimerWidget:
    """Test suite for TimerWidget."""

    @pytest.mark.asyncio
    async def test_timer_widget_initializes(self):
        """Test timer widget initializes correctly."""
        timer = PomodoroTimer()
        widget = TimerWidget(timer, id='test-timer')

        assert widget.timer == timer

    @pytest.mark.asyncio
    async def test_timer_widget_inactive_display(self):
        """Test timer widget shows inactive state."""
        timer = PomodoroTimer()
        widget = TimerWidget(timer, id='test-timer')

        # Timer not started
        assert not widget.is_active()
        assert widget.get_remaining_time() == 0

    @pytest.mark.asyncio
    async def test_timer_widget_active_display(self):
        """Test timer widget shows active state."""
        import time

        timer = PomodoroTimer()
        widget = TimerWidget(timer, id='test-timer')

        # Start timer manually (preset 0: 25 min work, 5 min break)
        timer.istimer = True
        timer.worktime = 25 * 60
        timer.breaktime = 5 * 60
        timer.workendtime = int(time.time()) + timer.worktime

        assert widget.is_active()
        assert widget.get_remaining_time() > 0
        assert not widget.is_break()

    @pytest.mark.asyncio
    async def test_timer_widget_remaining_time(self):
        """Test getting remaining time."""
        import time

        timer = PomodoroTimer()
        widget = TimerWidget(timer, id='test-timer')

        # Not started
        assert widget.get_remaining_time() == 0

        # Start timer manually
        timer.istimer = True
        timer.worktime = 25 * 60
        timer.workendtime = int(time.time()) + timer.worktime
        remaining = widget.get_remaining_time()

        # Should be close to 25 minutes (1500 seconds)
        assert 1400 < remaining <= 1500


class TestWisdomTreeApp:
    """Test suite for WisdomTreeApp."""

    @pytest.mark.asyncio
    async def test_app_initializes(self, mock_config):
        """Test app initializes with config."""
        app = WisdomTreeApp(config=mock_config)

        assert app.config == mock_config
        assert app.state_manager is not None
        assert app.tree_manager is not None
        assert app.quote_manager is not None
        assert app.timer is not None

    @pytest.mark.asyncio
    async def test_app_renders(self, mock_config):
        """Test app renders without errors."""
        app = WisdomTreeApp(config=mock_config)

        async with app.run_test() as pilot:
            # App should start
            await pilot.pause()

            # Widgets should be present
            assert app.query_one('#tree')
            assert app.query_one('#quote')
            assert app.query_one('#timer')

    @pytest.mark.asyncio
    async def test_app_quit_action(self, mock_config):
        """Test app quit action."""
        app = WisdomTreeApp(config=mock_config)

        async with app.run_test() as pilot:
            # Press 'q' to quit
            await pilot.press('q')
            # App should exit cleanly

    @pytest.mark.asyncio
    async def test_app_new_quote_action(self, mock_config):
        """Test new quote action."""
        app = WisdomTreeApp(config=mock_config)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Get initial quote
            quote_widget = app.query_one('#quote', QuoteWidget)
            initial_quote = quote_widget.current_quote

            # Press 'r' for new quote
            await pilot.press('r')
            await pilot.pause()

            # Quote should be set (might be same due to randomness)
            assert len(quote_widget.current_quote) > 0

    @pytest.mark.asyncio
    async def test_app_timer_toggle(self, mock_config):
        """Test timer start/stop toggle."""
        app = WisdomTreeApp(config=mock_config)

        async with app.run_test() as pilot:
            await pilot.pause()

            timer_widget = app.query_one('#timer', TimerWidget)

            # Initially not active
            assert not timer_widget.is_active()

            # Press space to start
            await pilot.press('space')
            await pilot.pause()

            # Should be active now
            assert timer_widget.is_active()

            # Press space to stop
            await pilot.press('space')
            await pilot.pause()

            # Should be inactive again
            assert not timer_widget.is_active()

    @pytest.mark.asyncio
    async def test_app_volume_controls(self, mock_config):
        """Test volume up/down actions."""
        # Start with volume at 50 so we can test both increase and decrease
        mock_config.audio.effect_volume = 50
        app = WisdomTreeApp(config=mock_config)

        async with app.run_test() as pilot:
            await pilot.pause()

            initial_volume = app.config.audio.effect_volume

            # Volume up
            await pilot.press(']')
            await pilot.pause()
            assert app.config.audio.effect_volume == initial_volume + 5

            # Volume down
            await pilot.press('[')
            await pilot.pause()
            assert app.config.audio.effect_volume == initial_volume

    @pytest.mark.asyncio
    async def test_app_saves_state_on_exit(self, mock_config):
        """Test app saves tree age on exit."""
        app = WisdomTreeApp(config=mock_config)

        async with app.run_test() as pilot:
            await pilot.pause()

            # Grow the tree
            app.tree_manager.tree.grow()
            age = app.tree_manager.get_age()

            # Exit app
            await pilot.press('q')

        # State should have been saved (check in state manager)
        loaded_age = app.state_manager.load_tree_age()
        assert loaded_age == age
