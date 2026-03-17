"""Configuration manager -- JSON persistence."""

from __future__ import annotations

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "telegterm"
CONFIG_FILE = CONFIG_DIR / "config.json"
SESSION_FILE = CONFIG_DIR / "telegterm.session"
CACHE_DIR = Path.home() / ".cache" / "telegterm"
MEDIA_CACHE_DIR = CACHE_DIR / "media"
AVATAR_CACHE_DIR = CACHE_DIR / "avatars"


def _default_config() -> dict:
    return {
        "version": 1,
        "api_id": 0,
        "api_hash": "",
        "theme": "tokyo-night",
        "notifications_enabled": True,
        "media_auto_download": True,
        "message_load_limit": 50,
        "last_chat_id": None,
    }


class ConfigManager:
    def __init__(self, path: Path = CONFIG_FILE) -> None:
        self.path = path
        self._data: dict = _default_config()

    def load(self) -> None:
        if self.path.exists():
            self._data = json.loads(self.path.read_text())
        else:
            self._data = _default_config()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, indent=2))

    def ensure_cache_dirs(self) -> None:
        MEDIA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        AVATAR_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    @property
    def needs_api_setup(self) -> bool:
        return not self._data.get("api_id") or not self._data.get("api_hash")

    @property
    def api_id(self) -> int:
        return self._data.get("api_id", 0)

    @api_id.setter
    def api_id(self, value: int) -> None:
        self._data["api_id"] = value

    @property
    def api_hash(self) -> str:
        return self._data.get("api_hash", "")

    @api_hash.setter
    def api_hash(self, value: str) -> None:
        self._data["api_hash"] = value

    @property
    def theme(self) -> str:
        return self._data.get("theme", "tokyo-night")

    @theme.setter
    def theme(self, value: str) -> None:
        self._data["theme"] = value

    @property
    def message_load_limit(self) -> int:
        return self._data.get("message_load_limit", 50)

    @property
    def last_chat_id(self) -> int | None:
        return self._data.get("last_chat_id")

    @last_chat_id.setter
    def last_chat_id(self, value: int | None) -> None:
        self._data["last_chat_id"] = value

    @property
    def media_auto_download(self) -> bool:
        return self._data.get("media_auto_download", True)
