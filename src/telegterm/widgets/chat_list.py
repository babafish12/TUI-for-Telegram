"""Scrollable chat list widget."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static, ListView, ListItem
from textual.containers import Horizontal, Vertical
from rich.text import Text

from telegterm.models.chat import Chat
from telegterm.constants import ChatType


class ChatSelected(Message):
    def __init__(self, chat: Chat) -> None:
        super().__init__()
        self.chat = chat


class ChatListItem(ListItem):
    DEFAULT_CSS = """
    ChatListItem {
        height: 3;
        padding: 0 1;
    }
    ChatListItem:hover {
        background: $surface;
    }
    ChatListItem.-active {
        background: $panel;
    }
    """

    def __init__(self, chat: Chat, **kwargs) -> None:
        super().__init__(**kwargs)
        self.chat = chat

    def compose(self) -> ComposeResult:
        chat = self.chat
        type_icons = {
            ChatType.PRIVATE: "",
            ChatType.GROUP: "",
            ChatType.SUPERGROUP: "",
            ChatType.CHANNEL: "",
        }
        icon = type_icons.get(chat.chat_type, "")

        title_text = Text()
        title_text.append(f"{icon} {chat.title}", style="bold")
        if chat.unread_count > 0:
            title_text.append(f"  ({chat.unread_count})", style="bold #7aa2f7")

        time_text = Text(chat.display_time, style="dim")

        preview = Text()
        if chat.last_message_sender and chat.chat_type != ChatType.PRIVATE:
            preview.append(f"{chat.last_message_sender}: ", style="bold dim")
        preview.append(chat.preview_text, style="dim")

        with Horizontal(classes="chat-row"):
            yield Static(title_text, classes="chat-title")
            yield Static(time_text, classes="chat-time")
        yield Static(preview, classes="chat-preview")


class ChatList(Widget):
    DEFAULT_CSS = """
    ChatList {
        width: 100%;
        height: 100%;
    }
    ChatList ListView {
        width: 100%;
        height: 100%;
        background: $background;
    }
    ChatList .chat-row {
        height: 1;
        width: 100%;
    }
    ChatList .chat-title {
        width: 1fr;
    }
    ChatList .chat-time {
        width: auto;
        text-align: right;
    }
    ChatList .chat-preview {
        height: 1;
    }
    """

    BINDINGS = [
        Binding("enter", "select_chat", "Open", show=False),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._chats: list[Chat] = []

    def compose(self) -> ComposeResult:
        yield ListView(id="chat-listview")

    def set_chats(self, chats: list[Chat]) -> None:
        self._chats = chats
        listview = self.query_one("#chat-listview", ListView)
        listview.clear()
        for chat in chats:
            listview.append(ChatListItem(chat))

    def update_chat(self, chat: Chat) -> None:
        for i, c in enumerate(self._chats):
            if c.id == chat.id:
                self._chats[i] = chat
                break
        self.set_chats(sorted(
            self._chats,
            key=lambda c: c.last_message_date or c.last_message_date,
            reverse=True,
        ))

    @property
    def selected_chat(self) -> Chat | None:
        listview = self.query_one("#chat-listview", ListView)
        if listview.highlighted_child and isinstance(listview.highlighted_child, ChatListItem):
            return listview.highlighted_child.chat
        return None

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if isinstance(event.item, ChatListItem):
            self.post_message(ChatSelected(event.item.chat))

    def action_select_chat(self) -> None:
        chat = self.selected_chat
        if chat:
            self.post_message(ChatSelected(chat))
