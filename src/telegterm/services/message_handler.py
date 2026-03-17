"""Event handler bridge: Telethon events -> Textual messages."""

from __future__ import annotations

from textual.app import App
from textual.message import Message as TextualMessage

from telethon import events, TelegramClient
from telethon.tl.types import User

from telegterm.constants import MediaType
from telegterm.models.message import Message


class NewMessageReceived(TextualMessage):
    def __init__(self, message: Message) -> None:
        super().__init__()
        self.message = message


class MessageEdited(TextualMessage):
    def __init__(self, message: Message) -> None:
        super().__init__()
        self.message = message


class MessageDeleted(TextualMessage):
    def __init__(self, chat_id: int, message_ids: list[int]) -> None:
        super().__init__()
        self.chat_id = chat_id
        self.message_ids = message_ids


class TypingUpdate(TextualMessage):
    def __init__(self, chat_id: int, user_id: int, user_name: str, is_typing: bool) -> None:
        super().__init__()
        self.chat_id = chat_id
        self.user_id = user_id
        self.user_name = user_name
        self.is_typing = is_typing


class MessageHandler:
    def __init__(self, client: TelegramClient, app: App) -> None:
        self._client = client
        self._app = app
        self._me = None

    async def setup(self) -> None:
        self._me = await self._client.get_me()
        self._client.add_event_handler(
            self._on_new_message,
            events.NewMessage(),
        )
        self._client.add_event_handler(
            self._on_message_edited,
            events.MessageEdited(),
        )
        self._client.add_event_handler(
            self._on_message_deleted,
            events.MessageDeleted(),
        )
        self._client.add_event_handler(
            self._on_user_typing,
            events.UserUpdate(),
        )

    async def _on_new_message(self, event: events.NewMessage.Event) -> None:
        msg = event.message
        sender_name = ""
        sender_id = 0

        if msg.sender:
            if isinstance(msg.sender, User):
                sender_name = msg.sender.first_name or ""
                if msg.sender.last_name:
                    sender_name += f" {msg.sender.last_name}"
            else:
                sender_name = getattr(msg.sender, "title", "")
            sender_id = msg.sender.id

        chat_id = msg.chat_id or msg.peer_id

        message = Message(
            id=msg.id,
            chat_id=chat_id,
            sender_id=sender_id,
            sender_name=sender_name,
            text=msg.message or "",
            date=msg.date,
            is_outgoing=msg.out if msg.out is not None else (sender_id == self._me.id),
            raw=msg,
        )
        self._app.post_message(NewMessageReceived(message))

    async def _on_message_edited(self, event: events.MessageEdited.Event) -> None:
        msg = event.message
        sender_name = ""
        sender_id = 0

        if msg.sender:
            if isinstance(msg.sender, User):
                sender_name = msg.sender.first_name or ""
            else:
                sender_name = getattr(msg.sender, "title", "")
            sender_id = msg.sender.id

        chat_id = msg.chat_id or msg.peer_id

        message = Message(
            id=msg.id,
            chat_id=chat_id,
            sender_id=sender_id,
            sender_name=sender_name,
            text=msg.message or "",
            date=msg.date,
            edit_date=msg.edit_date,
            raw=msg,
        )
        self._app.post_message(MessageEdited(message))

    async def _on_message_deleted(self, event: events.MessageDeleted.Event) -> None:
        chat_id = event.chat_id or 0
        self._app.post_message(MessageDeleted(chat_id, event.deleted_ids))

    async def _on_user_typing(self, event: events.UserUpdate.Event) -> None:
        if event.typing:
            user = await self._client.get_entity(event.user_id)
            name = ""
            if isinstance(user, User):
                name = user.first_name or ""
            self._app.post_message(TypingUpdate(
                chat_id=event.chat_id or 0,
                user_id=event.user_id,
                user_name=name,
                is_typing=True,
            ))
