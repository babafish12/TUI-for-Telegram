"""Constants and enums for telegterm."""

from __future__ import annotations

from enum import Enum, auto


class ChatType(Enum):
    PRIVATE = auto()
    GROUP = auto()
    SUPERGROUP = auto()
    CHANNEL = auto()


class MediaType(Enum):
    NONE = auto()
    PHOTO = auto()
    VIDEO = auto()
    AUDIO = auto()
    VOICE = auto()
    DOCUMENT = auto()
    STICKER = auto()
    GIF = auto()
    VIDEO_NOTE = auto()
