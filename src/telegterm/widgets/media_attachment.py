"""Non-image media attachment display widget."""

from __future__ import annotations

import subprocess

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static
from textual import on
from rich.text import Text

from telegterm.models.message import Message
from telegterm.constants import MediaType


class MediaAttachment(Widget):
    DEFAULT_CSS = """
    MediaAttachment {
        width: 100%;
        height: 1;
        padding: 0 2;
    }
    MediaAttachment:hover {
        background: $panel;
    }
    MediaAttachment Static {
        color: $accent;
    }
    """

    can_focus = True

    def __init__(self, message: Message, **kwargs) -> None:
        super().__init__(**kwargs)
        self.message = message

    def compose(self) -> ComposeResult:
        msg = self.message
        text = Text()
        icons = {
            MediaType.AUDIO: "♪",
            MediaType.VOICE: "♪",
            MediaType.VIDEO: "▶",
            MediaType.VIDEO_NOTE: "▶",
            MediaType.DOCUMENT: "◆",
            MediaType.GIF: "◎",
        }
        icon = icons.get(msg.media_type, "◆")
        text.append(f"  {icon} ", style="bold")
        text.append(msg.media_label)
        if msg.media_path:
            text.append("  [Enter: Oeffnen]", style="dim")
        yield Static(text)

    def on_key(self, event) -> None:
        if event.key == "enter" and self.message.media_path:
            try:
                subprocess.Popen(
                    ["xdg-open", self.message.media_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except FileNotFoundError:
                self.notify("xdg-open nicht gefunden", severity="error")
