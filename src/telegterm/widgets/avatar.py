"""Chat/user avatar widget."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static
from rich.text import Text

AVATAR_COLORS = [
    "#f7768e", "#9ece6a", "#e0af68", "#7aa2f7",
    "#bb9af7", "#7dcfff", "#ff79c6", "#50fa7b",
]


class Avatar(Widget):
    DEFAULT_CSS = """
    Avatar {
        width: 3;
        height: 1;
    }
    """

    def __init__(self, name: str, entity_id: int = 0, **kwargs) -> None:
        super().__init__(**kwargs)
        self._name = name
        self._entity_id = entity_id

    def compose(self) -> ComposeResult:
        initials = self._get_initials()
        color = AVATAR_COLORS[self._entity_id % len(AVATAR_COLORS)]
        text = Text()
        text.append(f" {initials} ", style=f"bold on {color}")
        yield Static(text)

    def _get_initials(self) -> str:
        parts = self._name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        elif parts:
            return parts[0][0].upper()
        return "?"
