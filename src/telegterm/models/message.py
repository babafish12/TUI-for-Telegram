"""Message data model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from telegterm.constants import MediaType


@dataclass
class Message:
    id: int
    chat_id: int
    sender_id: int
    sender_name: str
    text: str
    date: datetime
    is_outgoing: bool = False
    is_read: bool = False
    media_type: MediaType = MediaType.NONE
    media_path: str | None = None
    media_size: int | None = None
    media_duration: int | None = None
    media_filename: str | None = None
    reply_to_id: int | None = None
    edit_date: datetime | None = None
    raw: object = field(default=None, repr=False)

    @property
    def display_time(self) -> str:
        return self.date.strftime("%H:%M")

    @property
    def has_media(self) -> bool:
        return self.media_type != MediaType.NONE

    @property
    def media_label(self) -> str:
        labels = {
            MediaType.PHOTO: "Foto",
            MediaType.VIDEO: "Video",
            MediaType.AUDIO: "Audio",
            MediaType.VOICE: "Sprachnachricht",
            MediaType.DOCUMENT: self.media_filename or "Dokument",
            MediaType.STICKER: "Sticker",
            MediaType.GIF: "GIF",
            MediaType.VIDEO_NOTE: "Videonachricht",
        }
        label = labels.get(self.media_type, "")
        if self.media_duration and self.media_type in (
            MediaType.VOICE, MediaType.AUDIO, MediaType.VIDEO, MediaType.VIDEO_NOTE
        ):
            mins, secs = divmod(self.media_duration, 60)
            label += f" {mins}:{secs:02d}"
        if self.media_size and self.media_type == MediaType.DOCUMENT:
            if self.media_size > 1_048_576:
                label += f" ({self.media_size / 1_048_576:.1f} MB)"
            else:
                label += f" ({self.media_size / 1024:.0f} KB)"
        return label
