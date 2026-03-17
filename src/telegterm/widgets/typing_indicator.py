"""Typing indicator widget."""

from __future__ import annotations

from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import Static


class TypingIndicator(Widget):
    DEFAULT_CSS = """
    TypingIndicator {
        height: 1;
        padding: 0 1;
        color: $text-muted;
        display: none;
    }
    TypingIndicator.-visible {
        display: block;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._typing_users: dict[int, str] = {}

    def compose(self) -> ComposeResult:
        yield Static("", id="typing-text")

    def set_typing(self, user_id: int, name: str, is_typing: bool) -> None:
        if is_typing:
            self._typing_users[user_id] = name
        else:
            self._typing_users.pop(user_id, None)

        self._update_display()

    def clear(self) -> None:
        self._typing_users.clear()
        self._update_display()

    def _update_display(self) -> None:
        if not self._typing_users:
            self.remove_class("-visible")
            return

        names = list(self._typing_users.values())
        if len(names) == 1:
            text = f"{names[0]} tippt..."
        elif len(names) == 2:
            text = f"{names[0]} und {names[1]} tippen..."
        else:
            text = f"{names[0]} und {len(names) - 1} weitere tippen..."

        self.query_one("#typing-text", Static).update(text)
        self.add_class("-visible")
