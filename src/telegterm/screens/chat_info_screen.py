"""Chat info screen -- chat details modal."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static, Button
from textual.containers import Vertical, Center
from textual import on
from rich.text import Text

from telegterm.models.chat import Chat
from telegterm.constants import ChatType


class ChatInfoScreen(ModalScreen[None]):
    CSS = """
    ChatInfoScreen {
        align: center middle;
    }
    ChatInfoScreen #info-container {
        width: 50;
        height: auto;
        max-height: 20;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }
    ChatInfoScreen .info-title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    ChatInfoScreen .info-row {
        height: 1;
        margin-bottom: 0;
    }
    ChatInfoScreen Button {
        width: 100%;
        margin-top: 1;
    }
    """

    def __init__(self, chat: Chat, **kwargs) -> None:
        super().__init__(**kwargs)
        self._chat = chat

    def compose(self) -> ComposeResult:
        chat = self._chat
        type_labels = {
            ChatType.PRIVATE: "Privat",
            ChatType.GROUP: "Gruppe",
            ChatType.SUPERGROUP: "Supergruppe",
            ChatType.CHANNEL: "Kanal",
        }

        with Center():
            with Vertical(id="info-container"):
                yield Static(chat.title, classes="info-title")
                yield Static(
                    f"Typ: {type_labels.get(chat.chat_type, 'Unbekannt')}",
                    classes="info-row",
                )
                yield Static(f"ID: {chat.id}", classes="info-row")
                if chat.unread_count:
                    yield Static(
                        f"Ungelesen: {chat.unread_count}",
                        classes="info-row",
                    )
                yield Button("Schliessen", variant="primary", id="close-btn")

    @on(Button.Pressed, "#close-btn")
    def _on_close(self) -> None:
        self.dismiss(None)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)
