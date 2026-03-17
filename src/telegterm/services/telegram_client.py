"""Telegram client service -- wraps Telethon."""

from __future__ import annotations

from pathlib import Path

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import (
    User, Chat, Channel,
    MessageMediaPhoto, MessageMediaDocument,
    DocumentAttributeFilename, DocumentAttributeAudio,
    DocumentAttributeVideo, DocumentAttributeSticker,
    DocumentAttributeAnimated,
)

from telegterm.constants import ChatType, MediaType
from telegterm.models.chat import Chat as ChatModel
from telegterm.models.message import Message as MessageModel
from telegterm.models.config import SESSION_FILE


class TelegramService:
    def __init__(self, api_id: int, api_hash: str, session_path: Path = SESSION_FILE) -> None:
        self.client = TelegramClient(
            str(session_path), api_id, api_hash,
            system_version="telegterm 0.1.0",
        )
        self._me: User | None = None

    async def connect(self) -> None:
        await self.client.connect()

    async def is_authorized(self) -> bool:
        return await self.client.is_user_authorized()

    async def send_code(self, phone: str):
        return await self.client.send_code_request(phone)

    async def sign_in(self, phone: str, code: str):
        try:
            result = await self.client.sign_in(phone, code)
            self._me = result
            return result
        except SessionPasswordNeededError:
            raise

    async def sign_in_2fa(self, password: str):
        result = await self.client.sign_in(password=password)
        self._me = result
        return result

    async def get_me(self) -> User:
        if not self._me:
            self._me = await self.client.get_me()
        return self._me

    async def get_dialogs(self, limit: int = 50) -> list[ChatModel]:
        dialogs = await self.client.get_dialogs(limit=limit)
        chats = []
        for d in dialogs:
            chat_type = self._resolve_chat_type(d.entity)
            last_msg = ""
            last_sender = ""
            if d.message and d.message.message:
                last_msg = d.message.message
            elif d.message and d.message.media:
                last_msg = self._media_preview(d.message)
            if d.message and d.message.sender:
                sender = d.message.sender
                if isinstance(sender, User):
                    last_sender = sender.first_name or ""
                else:
                    last_sender = getattr(sender, "title", "")

            chats.append(ChatModel(
                id=d.entity.id,
                title=d.title or "Unknown",
                chat_type=chat_type,
                unread_count=d.unread_count,
                last_message=last_msg,
                last_message_date=d.date,
                last_message_sender=last_sender,
                is_pinned=d.pinned,
                is_muted=d.archived,
                entity=d.entity,
            ))
        return chats

    async def get_messages(
        self, chat_id: int, limit: int = 50, offset_id: int = 0
    ) -> list[MessageModel]:
        me = await self.get_me()
        messages = await self.client.get_messages(
            chat_id, limit=limit, offset_id=offset_id
        )
        result = []
        for msg in messages:
            if msg.action:
                continue
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

            media_type, media_filename, media_size, media_duration = (
                self._parse_media(msg)
            )

            result.append(MessageModel(
                id=msg.id,
                chat_id=chat_id,
                sender_id=sender_id,
                sender_name=sender_name,
                text=msg.message or "",
                date=msg.date,
                is_outgoing=msg.out if msg.out is not None else (sender_id == me.id),
                media_type=media_type,
                media_filename=media_filename,
                media_size=media_size,
                media_duration=media_duration,
                reply_to_id=msg.reply_to.reply_to_msg_id if msg.reply_to else None,
                edit_date=msg.edit_date,
                raw=msg,
            ))
        result.reverse()
        return result

    async def send_message(self, chat_id: int, text: str):
        return await self.client.send_message(chat_id, text)

    async def mark_read(self, chat_id: int, message_id: int) -> None:
        await self.client.send_read_acknowledge(chat_id, max_id=message_id)

    async def search_messages(self, chat_id: int, query: str, limit: int = 20):
        messages = await self.client.get_messages(
            chat_id, search=query, limit=limit
        )
        me = await self.get_me()
        result = []
        for msg in messages:
            if msg.action:
                continue
            sender_name = ""
            sender_id = 0
            if msg.sender:
                if isinstance(msg.sender, User):
                    sender_name = msg.sender.first_name or ""
                else:
                    sender_name = getattr(msg.sender, "title", "")
                sender_id = msg.sender.id
            result.append(MessageModel(
                id=msg.id,
                chat_id=chat_id,
                sender_id=sender_id,
                sender_name=sender_name,
                text=msg.message or "",
                date=msg.date,
                is_outgoing=msg.out if msg.out is not None else (sender_id == me.id),
                raw=msg,
            ))
        result.reverse()
        return result

    async def download_media(self, message, path: str | Path | None = None):
        return await self.client.download_media(message, file=str(path) if path else None)

    async def download_profile_photo(self, entity, path: str | Path) -> str | None:
        result = await self.client.download_profile_photo(
            entity, file=str(path), download_big=False
        )
        return str(result) if result else None

    async def disconnect(self) -> None:
        if self.client.is_connected():
            await self.client.disconnect()

    @staticmethod
    def _resolve_chat_type(entity) -> ChatType:
        if isinstance(entity, User):
            return ChatType.PRIVATE
        elif isinstance(entity, Channel):
            if entity.megagroup:
                return ChatType.SUPERGROUP
            return ChatType.CHANNEL
        return ChatType.GROUP

    @staticmethod
    def _media_preview(msg) -> str:
        if isinstance(msg.media, MessageMediaPhoto):
            return "[Foto]"
        elif isinstance(msg.media, MessageMediaDocument):
            doc = msg.media.document
            if doc:
                for attr in doc.attributes:
                    if isinstance(attr, DocumentAttributeSticker):
                        return f"[Sticker {attr.alt or ''}]"
                    if isinstance(attr, DocumentAttributeAnimated):
                        return "[GIF]"
                    if isinstance(attr, DocumentAttributeAudio):
                        if attr.voice:
                            return "[Sprachnachricht]"
                        return "[Audio]"
                    if isinstance(attr, DocumentAttributeVideo):
                        if attr.round_message:
                            return "[Videonachricht]"
                        return "[Video]"
                return "[Dokument]"
        return "[Media]"

    @staticmethod
    def _parse_media(msg) -> tuple[MediaType, str | None, int | None, int | None]:
        if not msg.media:
            return MediaType.NONE, None, None, None

        if isinstance(msg.media, MessageMediaPhoto):
            return MediaType.PHOTO, None, None, None

        if isinstance(msg.media, MessageMediaDocument):
            doc = msg.media.document
            if not doc:
                return MediaType.DOCUMENT, None, None, None

            filename = None
            duration = None
            size = doc.size

            for attr in doc.attributes:
                if isinstance(attr, DocumentAttributeFilename):
                    filename = attr.file_name
                if isinstance(attr, DocumentAttributeSticker):
                    return MediaType.STICKER, None, size, None
                if isinstance(attr, DocumentAttributeAnimated):
                    return MediaType.GIF, None, size, None
                if isinstance(attr, DocumentAttributeAudio):
                    if attr.voice:
                        return MediaType.VOICE, None, size, attr.duration
                    return MediaType.AUDIO, filename, size, attr.duration
                if isinstance(attr, DocumentAttributeVideo):
                    if attr.round_message:
                        return MediaType.VIDEO_NOTE, None, size, attr.duration
                    return MediaType.VIDEO, filename, size, attr.duration

            return MediaType.DOCUMENT, filename, size, None

        return MediaType.NONE, None, None, None
