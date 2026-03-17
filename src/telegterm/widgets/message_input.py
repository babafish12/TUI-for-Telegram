"""Message input widget."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import TextArea
from textual.events import Key


class MessageSubmitted(Message):
    def __init__(self, text: str) -> None:
        super().__init__()
        self.text = text


class MessageInput(Widget):
    DEFAULT_CSS = """
    MessageInput {
        height: auto;
        min-height: 3;
        max-height: 8;
        dock: bottom;
        padding: 0 1;
    }
    MessageInput TextArea {
        height: auto;
        min-height: 1;
        max-height: 6;
        background: $panel;
        border: tall $panel;
    }
    MessageInput TextArea:focus {
        border: tall $primary;
    }
    """

    def compose(self) -> ComposeResult:
        yield TextArea(id="msg-textarea", language=None)

    def on_mount(self) -> None:
        ta = self.query_one("#msg-textarea", TextArea)
        ta.show_line_numbers = False

    def on_key(self, event: Key) -> None:
        if event.key == "enter" and not event.shift:
            ta = self.query_one("#msg-textarea", TextArea)
            text = ta.text.strip()
            if text:
                self.post_message(MessageSubmitted(text))
                ta.clear()
            event.prevent_default()
            event.stop()

    def focus_input(self) -> None:
        self.query_one("#msg-textarea", TextArea).focus()
