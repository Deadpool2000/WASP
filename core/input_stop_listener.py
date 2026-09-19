import threading
import time

from PyQt6.QtCore import QObject, pyqtSignal
from pynput import keyboard, mouse


class InputStopListener(QObject):
    """Listen for physical user input and request activity stop."""

    stop_triggered = pyqtSignal()
    status_update = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._lock = threading.RLock()
        self._enabled = False
        self._activity_active = False
        self._ignore_until = 0.0
        self._mouse_listener = None
        self._keyboard_listener = None

    def set_enabled(self, enabled):
        """Enable or disable global mouse and keyboard listeners."""
        if enabled:
            self._start_listeners()
        else:
            self.stop()
            self.status_update.emit("Stop on user input disabled")

    def set_activity_active(self, active):
        """Set whether input events can stop the current activity run."""
        with self._lock:
            self._activity_active = active

    def ignore_for(self, seconds):
        """Ignore input briefly after a start or settings click."""
        with self._lock:
            self._ignore_until = max(self._ignore_until, time.monotonic() + seconds)

    def _start_listeners(self):
        with self._lock:
            if self._enabled:
                return

            self._enabled = True
            self._mouse_listener = mouse.Listener(
                on_move=self._on_mouse_move,
                on_click=self._on_mouse_click,
            )
            self._keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press,
            )
            listeners = (self._mouse_listener, self._keyboard_listener)

        try:
            for listener in listeners:
                listener.start()
        except Exception as error:
            self.stop()
            self.status_update.emit(f"Input listener error: {error}")
            return

        self.status_update.emit("Stop on user input enabled")

    def stop(self):
        """Stop global listeners and ignore callbacks already in flight."""
        with self._lock:
            self._enabled = False
            listeners = (self._mouse_listener, self._keyboard_listener)
            self._mouse_listener = None
            self._keyboard_listener = None

        for listener in listeners:
            if listener is not None:
                listener.stop()

    def _is_user_input(self, injected=False):
        """Return whether callback should stop activity.

        pynput marks injected events on supported backends. Ignoring them
        prevents WASP's own pyautogui events from stopping its activity.
        """
        with self._lock:
            return (
                self._enabled
                and self._activity_active
                and time.monotonic() >= self._ignore_until
                and not injected
            )

    def _on_mouse_move(self, _x, _y, injected=False):
        if self._is_user_input(injected):
            self.stop_triggered.emit()

    def _on_mouse_click(self, _x, _y, _button, pressed, injected=False):
        if pressed and self._is_user_input(injected):
            self.stop_triggered.emit()

    def _on_key_press(self, _key, injected=False):
        if self._is_user_input(injected):
            self.stop_triggered.emit()
