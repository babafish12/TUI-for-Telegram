"""Single message bubble widget."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static
from textual.containers import Vertical
from rich.text import Text

from telegterm.models.message import Message
from telegterm.constants import MediaType


class MessageBubble(Widget):
    DEFAULT_CSS = """
    MessageBubble {
        width: 100%;
        height: auto;
        padding: 0 1;
        margin: 0 0 0 0;
    }
    MessageBubble:hover {
        background: $surface;
    }
    MessageBubble.-outgoing .msg-header {
        color: $success;
    }
    MessageBubble.-incoming .msg-header {
        color: $primary;
    }
    MessageBubble .msg-header {
        height: 1;
    }
    MessageBubble .msg-text {
        height: auto;
        padding: 0 0 0 2;
    }
    MessageBubble .msg-media {
        height: auto;
        padding: 0 0 0 2;
        color: $accent;
    }
    """

    can_focus = True

    def __init__(self, message: Message, **kwargs) -> None:
        super().__init__(**kwargs)
        self.message = message

    def compose(self) -> ComposeResult:
        msg = self.message

        header = Text()
        header.append(msg.sender_name, style="bold")
        header.append(f"  {msg.display_time}", style="dim")
        if msg.edit_date:
            header.append(" (bearbeitet)", style="dim italic")

        with Vertical():
            yield Static(header, classes="msg-header")

            if msg.has_media:
                media_text = Text()
                media_text.append(f"  {msg.media_label}", style="bold")
                yield Static(media_text, classes="msg-media")

            if msg.text:
                yield Static(msg.text, classes="msg-text")

    def on_mount(self) -> None:
        if self.message.is_outgoing:
            self.add_class("-outgoing")
        else:
            self.add_class("-incoming")
