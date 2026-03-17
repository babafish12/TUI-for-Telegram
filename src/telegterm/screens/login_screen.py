"""Login screen -- phone number, code, optional 2FA."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static, Input, Button
from textual.containers import Vertical, Center
from textual import on, work

from telethon.errors import SessionPasswordNeededError


class LoginScreen(ModalScreen[bool]):
    CSS = """
    LoginScreen {
        align: center middle;
    }
    LoginScreen #login-container {
        width: 56;
        height: auto;
        max-height: 22;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }
    LoginScreen .login-title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    LoginScreen .login-subtitle {
        text-align: center;
        color: $text-muted;
        margin-bottom: 1;
    }
    LoginScreen Input {
        margin-bottom: 1;
    }
    LoginScreen .login-error {
        color: $error;
        text-align: center;
        margin-bottom: 1;
    }
    LoginScreen Button {
        width: 100%;
        margin-top: 1;
    }
    LoginScreen .hidden {
        display: none;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._step = 1
        self._phone = ""
        self._phone_code_hash = ""

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="login-container"):
                yield Static("telegterm Login", classes="login-title")
                yield Static(
                    "Telefonnummer eingeben (z.B. +49...)",
                    id="subtitle",
                    classes="login-subtitle",
                )
                yield Input(
                    placeholder="+49123456789",
                    id="phone-input",
                )
                yield Input(
                    placeholder="Code aus Telegram",
                    id="code-input",
                    classes="hidden",
                )
                yield Input(
                    placeholder="2FA Passwort",
                    password=True,
                    id="password-input",
                    classes="hidden",
                )
                yield Static("", id="error-msg", classes="login-error")
                yield Button("Code senden", variant="primary", id="action-btn")

    def on_mount(self) -> None:
        self.query_one("#phone-input", Input).focus()

    @on(Button.Pressed, "#action-btn")
    def _on_action(self) -> None:
        if self._step == 1:
            self._send_code()
        elif self._step == 2:
            self._verify_code()
        elif self._step == 3:
            self._verify_2fa()

    @on(Input.Submitted)
    def _on_submit(self) -> None:
        self._on_action()

    @work()
    async def _send_code(self) -> None:
        phone = self.query_one("#phone-input", Input).value.strip()
        error = self.query_one("#error-msg", Static)

        if not phone:
            error.update("Telefonnummer eingeben")
            return

        self._phone = phone
        btn = self.query_one("#action-btn", Button)
        btn.label = "Sende..."
        btn.disabled = True

        try:
            result = await self.app.telegram_service.send_code(phone)
            self._phone_code_hash = result.phone_code_hash

            self._step = 2
            self.query_one("#phone-input").add_class("hidden")
            self.query_one("#code-input").remove_class("hidden")
            self.query_one("#subtitle", Static).update("Code eingeben")
            btn.label = "Anmelden"
            btn.disabled = False
            error.update("")
            self.query_one("#code-input", Input).focus()
        except Exception as e:
            error.update(str(e))
            btn.label = "Code senden"
            btn.disabled = False

    @work()
    async def _verify_code(self) -> None:
        code = self.query_one("#code-input", Input).value.strip()
        error = self.query_one("#error-msg", Static)

        if not code:
            error.update("Code eingeben")
            return

        btn = self.query_one("#action-btn", Button)
        btn.label = "Pruefe..."
        btn.disabled = True

        try:
            await self.app.telegram_service.sign_in(self._phone, code)
            self.dismiss(True)
        except SessionPasswordNeededError:
            self._step = 3
            self.query_one("#code-input").add_class("hidden")
            self.query_one("#password-input").remove_class("hidden")
            self.query_one("#subtitle", Static).update("2FA Passwort eingeben")
            btn.label = "Anmelden"
            btn.disabled = False
            error.update("")
            self.query_one("#password-input", Input).focus()
        except Exception as e:
            error.update(str(e))
            btn.label = "Anmelden"
            btn.disabled = False

    @work()
    async def _verify_2fa(self) -> None:
        password = self.query_one("#password-input", Input).value
        error = self.query_one("#error-msg", Static)

        if not password:
            error.update("Passwort eingeben")
            return

        btn = self.query_one("#action-btn", Button)
        btn.label = "Pruefe..."
        btn.disabled = True

        try:
            await self.app.telegram_service.sign_in_2fa(password)
            self.dismiss(True)
        except Exception as e:
            error.update(str(e))
            btn.label = "Anmelden"
            btn.disabled = False
