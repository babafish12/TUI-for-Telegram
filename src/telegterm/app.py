"""Main Textual application."""

from __future__ import annotations

from textual.app import App
from textual import work

from telegterm.models.config import ConfigManager
from telegterm.services.telegram_client import TelegramService
from telegterm.services.message_handler import MessageHandler
from telegterm.services.media_manager import MediaManager
from telegterm.screens.api_setup_screen import ApiSetupScreen
from telegterm.screens.login_screen import LoginScreen
from telegterm.screens.main_screen import MainScreen
from telegterm.theme import THEMES


class TelegtermApp(App):
    CSS = """
    Screen {
        background: $background;
        color: $foreground;
    }
    Input {
        background: $panel;
        color: $foreground;
        border: tall $panel;
    }
    Input:focus {
        border: tall $primary;
    }
    Button {
        background: $surface;
        color: $foreground;
        border: tall $panel;
    }
    Button:hover {
        background: $panel;
    }
    Button.-primary {
        background: $primary;
        color: $background;
    }
    ListView {
        background: $background;
    }
    ListView > ListItem {
        background: $background;
    }
    ListView > ListItem.-highlight {
        background: $surface;
    }
    TextArea {
        background: $panel;
        color: $foreground;
    }
    Toast {
        background: $surface;
        color: $foreground;
    }
    """

    TITLE = "telegterm"

    def __init__(self) -> None:
        super().__init__()
        self.config_manager = ConfigManager()
        self.telegram_service: TelegramService | None = None
        self.message_handler: MessageHandler | None = None
        self.media_manager = MediaManager()

    def on_mount(self) -> None:
        self.config_manager.load()
        self.config_manager.ensure_cache_dirs()

        for t in THEMES:
            self.register_theme(t)
        self.theme = self.config_manager.theme

        if self.config_manager.needs_api_setup:
            self.push_screen(ApiSetupScreen(), callback=self._on_api_setup)
        else:
            self._init_telegram()

    def _on_api_setup(self, result: bool) -> None:
        if result:
            self._init_telegram()
        else:
            self.exit()

    def _init_telegram(self) -> None:
        self.telegram_service = TelegramService(
            api_id=self.config_manager.api_id,
            api_hash=self.config_manager.api_hash,
        )
        self.message_handler = MessageHandler(
            self.telegram_service.client, self
        )
        self._connect_and_auth()

    @work()
    async def _connect_and_auth(self) -> None:
        await self.telegram_service.connect()

        if await self.telegram_service.is_authorized():
            self.push_screen(MainScreen())
        else:
            self.push_screen(LoginScreen(), callback=self._on_login)

    def _on_login(self, result: bool) -> None:
        if result:
            self.push_screen(MainScreen())
        else:
            self.exit()

    @work()
    async def _cleanup(self) -> None:
        if self.telegram_service:
            await self.telegram_service.disconnect()

    def on_unmount(self) -> None:
        self._cleanup()
