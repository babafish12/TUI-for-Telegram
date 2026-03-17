"""Settings screen -- theme selection, logout."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static, Button, Select
from textual.containers import Vertical, Center
from textual import on

from telegterm.theme import THEME_NAMES


class SettingsScreen(ModalScreen[str | None]):
    CSS = """
    SettingsScreen {
        align: center middle;
    }
    SettingsScreen #settings-container {
        width: 50;
        height: auto;
        max-height: 20;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }
    SettingsScreen .settings-title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    SettingsScreen .settings-label {
        margin-top: 1;
        margin-bottom: 0;
    }
    SettingsScreen Button {
        width: 100%;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="settings-container"):
                yield Static("Einstellungen", classes="settings-title")
                yield Static("Theme:", classes="settings-label")
                yield Select(
                    [(name, name) for name in THEME_NAMES],
                    value=self.app.theme,
                    id="theme-select",
                )
                yield Button("Schliessen", variant="primary", id="close-btn")
                yield Button("Abmelden", variant="error", id="logout-btn")

    @on(Select.Changed, "#theme-select")
    def _on_theme_changed(self, event: Select.Changed) -> None:
        if event.value:
            self.app.theme = event.value
            self.app.config_manager.theme = event.value
            self.app.config_manager.save()

    @on(Button.Pressed, "#close-btn")
    def _on_close(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#logout-btn")
    def _on_logout(self) -> None:
        self.dismiss("logout")

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)
