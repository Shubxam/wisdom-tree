"""Timer widget for Pomodoro timer display."""

import time

from textual.widgets import Static

from wisdom_tree.timer import PomodoroTimer


class TimerWidget(Static):
    """Display Pomodoro timer status and countdown."""

    def __init__(self, timer: PomodoroTimer, **kwargs):
        """Initialize timer widget.

        Args:
            timer: Pomodoro timer instance
            **kwargs: Additional widget arguments
        """
        super().__init__(**kwargs)
        self.timer = timer

    def on_mount(self) -> None:
        """Set up periodic timer display updates when widget is mounted."""
        self.set_interval(1.0, self.update_timer_display)

    def update_timer_display(self) -> None:
        """Update the timer display with current state."""
        if not self.timer.istimer:
            self.update('Press SPACE to start')
            return

        # Timer is active
        if self.timer.isbreak:
            remaining = self.timer.breakendtime - time.time()
            status = 'Break'
        else:
            remaining = self.timer.workendtime - time.time()
            status = 'Focus'

        if remaining > 0:
            mins, secs = divmod(int(remaining), 60)
            self.update(f'{status}: {mins:02d}:{secs:02d}')
        else:
            self.update('Complete!')
            # Timer will be reset by the main app

    def is_active(self) -> bool:
        """Check if timer is currently running.

        Returns:
            True if timer is active
        """
        return self.timer.istimer

    def is_break(self) -> bool:
        """Check if currently in break period.

        Returns:
            True if in break period
        """
        return self.timer.isbreak

    def get_remaining_time(self) -> int:
        """Get remaining time in seconds.

        Returns:
            Remaining seconds, or 0 if timer not active
        """
        if not self.timer.istimer:
            return 0

        if self.timer.isbreak:
            return max(0, int(self.timer.breakendtime - time.time()))
        else:
            return max(0, int(self.timer.workendtime - time.time()))
