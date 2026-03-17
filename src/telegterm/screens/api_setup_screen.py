"""API credentials setup screen -- first-run only."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static, Input, Button
from textual.containers import Vertical, Center
from textual import on


class ApiSetupScreen(ModalScreen[bool]):
    CSS = """
    ApiSetupScreen {
        align: center middle;
    }
    ApiSetupScreen #setup-container {
        width: 64;
        height: auto;
        max-height: 24;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }
    ApiSetupScreen .setup-title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    ApiSetupScreen .setup-info {
        text-align: center;
        color: $text-muted;
        margin-bottom: 1;
    }
    ApiSetupScreen Input {
        margin-bottom: 1;
    }
    ApiSetupScreen .setup-error {
        color: $error;
        text-align: center;
        margin-bottom: 1;
    }
    ApiSetupScreen Button {
        width: 100%;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="setup-container"):
                yield Static("telegterm", classes="setup-title")
                yield Static(
                    "Telegram API Credentials eingeben\n"
                    "Erstelle diese auf my.telegram.org",
                    classes="setup-info",
                )
                yield Input(placeholder="API ID (Zahl)", id="api-id")
                yield Input(placeholder="API Hash", id="api-hash")
                yield Static("", id="error-msg", classes="setup-error")
                yield Button("Weiter", variant="primary", id="save-btn")

    def on_mount(self) -> None:
        self.query_one("#api-id", Input).focus()

    @on(Button.Pressed, "#save-btn")
    def _on_save(self) -> None:
        self._validate_and_save()

    @on(Input.Submitted)
    def _on_submit(self) -> None:
        self._validate_and_save()

    def _validate_and_save(self) -> None:
        api_id_str = self.query_one("#api-id", Input).value.strip()
        api_hash = self.query_one("#api-hash", Input).value.strip()
        error = self.query_one("#error-msg", Static)

        if not api_id_str:
            error.update("API ID darf nicht leer sein")
            return

        try:
            api_id = int(api_id_str)
        except ValueError:
            error.update("API ID muss eine Zahl sein")
            return

        if not api_hash:
            error.update("API Hash darf nicht leer sein")
            return

        if len(api_hash) < 10:
            error.update("API Hash sieht ungueltig aus")
            return

        self.app.config_manager.api_id = api_id
        self.app.config_manager.api_hash = api_hash
        self.app.config_manager.save()
        self.dismiss(True)
