"""Chat data model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from telegterm.constants import ChatType


@dataclass
class Chat:
    id: int
    title: str
    chat_type: ChatType
    unread_count: int = 0
    last_message: str = ""
    last_message_date: datetime | None = None
    last_message_sender: str = ""
    is_pinned: bool = False
    is_muted: bool = False
    avatar_path: str | None = None
    entity: object = field(default=None, repr=False)

    @property
    def display_time(self) -> str:
        if not self.last_message_date:
            return ""
        now = datetime.now(tz=self.last_message_date.tzinfo)
        delta = now - self.last_message_date
        if delta.days == 0:
            return self.last_message_date.strftime("%H:%M")
        elif delta.days < 7:
            return self.last_message_date.strftime("%a")
        else:
            return self.last_message_date.strftime("%d.%m")

    @property
    def preview_text(self) -> str:
        text = self.last_message.replace("\n", " ")
        if len(text) > 40:
            return text[:37] + "..."
        return text
