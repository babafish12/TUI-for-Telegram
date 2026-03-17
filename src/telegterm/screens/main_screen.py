"""Main screen -- chat list sidebar + message view + input."""

from __future__ import annotations

import subprocess

import pyperclip
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.containers import Horizontal, Vertical
from textual.widgets import Static
from textual import on, work

from telegterm.widgets.chat_list import ChatList, ChatSelected
from telegterm.widgets.message_view import MessageView
from telegterm.widgets.message_bubble import MessageBubble
from telegterm.widgets.message_input import MessageInput, MessageSubmitted
from telegterm.widgets.typing_indicator import TypingIndicator
from telegterm.widgets.status_bar import StatusBar
from telegterm.services.message_handler import (
    NewMessageReceived,
    MessageEdited,
    MessageDeleted,
    TypingUpdate,
)
from telegterm.theme import next_theme
from telegterm.constants import MediaType


class MainScreen(Screen):
    CSS = """
    MainScreen {
        layout: horizontal;
    }
    #sidebar {
        width: 35;
        min-width: 25;
        height: 100%;
        border-right: tall $panel;
    }
    #sidebar-header {
        height: 1;
        background: $surface;
        padding: 0 1;
        text-style: bold;
        color: $primary;
    }
    #chat-area {
        width: 1fr;
        height: 100%;
    }
    #chat-header {
        height: 1;
        background: $surface;
        padding: 0 1;
        text-style: bold;
    }
    """

    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("tab", "switch_focus", "Focus", show=False),
        Binding("slash", "search", "Search", show=False),
        Binding("y", "copy_message", "Copy", show=False),
        Binding("shift+y", "copy_media", "Copy media", show=False, key_display="Y"),
        Binding("g", "scroll_bottom", "Bottom", show=False),
        Binding("T", "cycle_theme", "Theme", show=False),
        Binding("q", "quit", "Quit", show=False),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._current_chat_id: int | None = None
        self._current_chat_title: str = ""

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Static("telegterm", id="sidebar-header")
                yield ChatList(id="chat-list")
            with Vertical(id="chat-area"):
                yield Static("", id="chat-header")
                yield MessageView(id="message-view")
                yield TypingIndicator(id="typing")
                yield MessageInput(id="message-input")
        yield StatusBar(id="status-bar")

    @work()
    async def on_mount(self) -> None:
        self.query_one("#status-bar", StatusBar).set_context("main")
        await self._load_chats()
        await self.app.message_handler.setup()

    @work()
    async def _load_chats(self) -> None:
        try:
            chats = await self.app.telegram_service.get_dialogs(limit=80)
            chat_list = self.query_one("#chat-list", ChatList)
            chat_list.set_chats(chats)
        except Exception as e:
            self.notify(f"Fehler beim Laden: {e}", severity="error")

    @on(ChatSelected)
    def _on_chat_selected(self, event: ChatSelected) -> None:
        self._current_chat_id = event.chat.id
        self._current_chat_title = event.chat.title
        self.query_one("#chat-header", Static).update(event.chat.title)
        self.query_one("#typing", TypingIndicator).clear()
        self.query_one("#status-bar", StatusBar).set_context("chat")
        self._load_messages(event.chat.id)

    @work()
    async def _load_messages(self, chat_id: int) -> None:
        try:
            messages = await self.app.telegram_service.get_messages(
                chat_id,
                limit=self.app.config_manager.message_load_limit,
            )
            msg_view = self.query_one("#message-view", MessageView)
            msg_view.set_messages(messages)

            if messages:
                await self.app.telegram_service.mark_read(chat_id, messages[-1].id)
        except Exception as e:
            self.notify(f"Fehler: {e}", severity="error")

    @on(MessageSubmitted)
    def _on_message_submitted(self, event: MessageSubmitted) -> None:
        if self._current_chat_id:
            self._send_message(event.text)

    @work()
    async def _send_message(self, text: str) -> None:
        try:
            await self.app.telegram_service.send_message(self._current_chat_id, text)
        except Exception as e:
            self.notify(f"Senden fehlgeschlagen: {e}", severity="error")

    def on_new_message_received(self, event: NewMessageReceived) -> None:
        msg = event.message
        if msg.chat_id == self._current_chat_id:
            self.query_one("#message-view", MessageView).append_message(msg)
            self._mark_as_read(msg.chat_id, msg.id)

        self._refresh_chat_preview(msg.chat_id, msg.text, msg.sender_name)

    @work()
    async def _mark_as_read(self, chat_id: int, msg_id: int) -> None:
        try:
            await self.app.telegram_service.mark_read(chat_id, msg_id)
        except Exception:
            pass

    def _refresh_chat_preview(self, chat_id: int, text: str, sender: str) -> None:
        chat_list = self.query_one("#chat-list", ChatList)
        for chat in chat_list._chats:
            if chat.id == chat_id:
                chat.last_message = text
                chat.last_message_sender = sender
                if chat_id != self._current_chat_id:
                    chat.unread_count += 1
                break

    def on_message_edited(self, event: MessageEdited) -> None:
        pass

    def on_message_deleted(self, event: MessageDeleted) -> None:
        pass

    def on_typing_update(self, event: TypingUpdate) -> None:
        if event.chat_id == self._current_chat_id:
            indicator = self.query_one("#typing", TypingIndicator)
            indicator.set_typing(event.user_id, event.user_name, event.is_typing)

    def action_switch_focus(self) -> None:
        focused = self.app.focused
        msg_input = self.query_one("#message-input", MessageInput)
        chat_list = self.query_one("#chat-list", ChatList)

        if focused and focused.is_descendant_of(self.query_one("#sidebar")):
            msg_input.focus_input()
        else:
            listview = chat_list.query_one("#chat-listview")
            listview.focus()

    def action_cursor_down(self) -> None:
        listview = self.query_one("#chat-list ChatList #chat-listview")
        listview.action_cursor_down()

    def action_cursor_up(self) -> None:
        listview = self.query_one("#chat-list ChatList #chat-listview")
        listview.action_cursor_up()

    def action_copy_message(self) -> None:
        msg_view = self.query_one("#message-view", MessageView)
        msg = msg_view.focused_message
        if msg and msg.text:
            try:
                pyperclip.copy(msg.text)
                self.notify("Nachricht kopiert")
            except Exception:
                self.notify("Kopieren fehlgeschlagen", severity="error")
        else:
            self.notify("Keine Nachricht ausgewaehlt", severity="warning")

    def action_copy_media(self) -> None:
        msg_view = self.query_one("#message-view", MessageView)
        msg = msg_view.focused_message
        if msg and msg.media_path:
            try:
                pyperclip.copy(msg.media_path)
                self.notify("Medienpfad kopiert")
            except Exception:
                self.notify("Kopieren fehlgeschlagen", severity="error")
        else:
            self.notify("Kein Medium ausgewaehlt", severity="warning")

    def action_scroll_bottom(self) -> None:
        self.query_one("#message-view", MessageView)._scroll_to_bottom()

    def action_cycle_theme(self) -> None:
        new_theme = next_theme(self.app.theme)
        self.app.theme = new_theme
        self.app.config_manager.theme = new_theme
        self.app.config_manager.save()
        self.notify(f"Theme: {new_theme}")

    def action_search(self) -> None:
        self.notify("Suche kommt bald", severity="information")

    def action_quit(self) -> None:
        self.app.exit()
