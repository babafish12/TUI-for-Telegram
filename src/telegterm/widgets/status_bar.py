"""Bottom status/hint bar."""

from __future__ import annotations

from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import Static
from rich.text import Text


class StatusBar(Widget):
    DEFAULT_CSS = """
    StatusBar {
        dock: bottom;
        height: 1;
        background: $surface;
        padding: 0 1;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._hints = ""

    def compose(self) -> ComposeResult:
        yield Static(self._build_hints(), id="hints")

    def set_context(self, context: str = "main") -> None:
        self._hints = context
        try:
            self.query_one("#hints", Static).update(self._build_hints())
        except Exception:
            pass

    def _build_hints(self) -> Text:
        hints = Text()
        keys = {
            "main": [
                ("j/k", "Navigate"),
                ("Enter", "Open"),
                ("Tab", "Focus"),
                ("/", "Search"),
                ("y", "Copy"),
                ("T", "Theme"),
                ("q", "Quit"),
            ],
            "chat": [
                ("Enter", "Send"),
                ("Tab", "Focus"),
                ("y", "Copy msg"),
                ("Y", "Copy media"),
                ("Esc", "Back"),
                ("/", "Search"),
            ],
        }
        for key, label in keys.get(self._hints, keys["main"]):
            hints.append(f" {key} ", style="bold reverse")
            hints.append(f" {label} ", style="dim")
        return hints
