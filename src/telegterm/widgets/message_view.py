"""Scrollable message view widget."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static
from textual.containers import VerticalScroll

from telegterm.models.message import Message
from telegterm.widgets.message_bubble import MessageBubble


class MessageView(Widget):
    DEFAULT_CSS = """
    MessageView {
        width: 100%;
        height: 1fr;
    }
    MessageView #msg-scroll {
        width: 100%;
        height: 100%;
        background: $background;
    }
    MessageView #empty-hint {
        width: 100%;
        height: 100%;
        content-align: center middle;
        color: $text-muted;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._messages: list[Message] = []

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="msg-scroll"):
            yield Static(
                "Chat auswaehlen um Nachrichten zu sehen",
                id="empty-hint",
            )

    def set_messages(self, messages: list[Message]) -> None:
        self._messages = messages
        scroll = self.query_one("#msg-scroll", VerticalScroll)
        scroll.remove_children()

        if not messages:
            scroll.mount(Static(
                "Keine Nachrichten",
                id="empty-hint",
            ))
            return

        for msg in messages:
            scroll.mount(MessageBubble(msg))

        self.call_after_refresh(self._scroll_to_bottom)

    def append_message(self, message: Message) -> None:
        self._messages.append(message)
        scroll = self.query_one("#msg-scroll", VerticalScroll)

        hint = scroll.query("#empty-hint")
        if hint:
            hint.first().remove()

        scroll.mount(MessageBubble(message))
        self.call_after_refresh(self._scroll_to_bottom)

    def _scroll_to_bottom(self) -> None:
        scroll = self.query_one("#msg-scroll", VerticalScroll)
        scroll.scroll_end(animate=False)

    @property
    def focused_message(self) -> Message | None:
        focused = self.app.focused
        if isinstance(focused, MessageBubble):
            return focused.message
        return None

    @property
    def messages(self) -> list[Message]:
        return self._messages
