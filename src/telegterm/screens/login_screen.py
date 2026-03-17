"""Login screen -- QR code (default) + phone number fallback."""

from __future__ import annotations

import io

import segno
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static, Input, Button
from textual.containers import Vertical, Center
from textual import on, work

from telethon.errors import SessionPasswordNeededError


def _render_qr(url: str) -> str:
    """Render QR code as compact Unicode string for terminal display."""
    qr = segno.make(url)
    buf = io.StringIO()
    qr.terminal(out=buf, compact=True)
    return buf.getvalue()


class LoginScreen(ModalScreen[bool]):
    CSS = """
    LoginScreen {
        align: center middle;
    }
    LoginScreen #login-container {
        width: 60;
        height: auto;
        max-height: 32;
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
    LoginScreen #qr-display {
        text-align: center;
        margin: 1 0;
        height: auto;
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
        self._mode = "qr"  # "qr" or "phone"
        self._phone_step = 1  # 1=phone, 2=code, 3=2fa
        self._phone = ""
        self._qr_login = None

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="login-container"):
                yield Static("telegterm Login", classes="login-title")
                yield Static(
                    "QR-Code mit Telegram-App scannen",
                    id="subtitle",
                    classes="login-subtitle",
                )
                # QR mode widgets
                yield Static("Lade QR-Code...", id="qr-display")
                # Phone mode widgets (hidden by default)
                yield Input(
                    placeholder="+49123456789",
                    id="phone-input",
                    classes="hidden",
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
                # Phone mode action button (hidden in QR mode)
                yield Button(
                    "Code senden",
                    variant="primary",
                    id="action-btn",
                    classes="hidden",
                )
                # Mode switch button
                yield Button(
                    "Mit Telefonnummer anmelden",
                    id="switch-btn",
                )

    def on_mount(self) -> None:
        self._start_qr_login()

    # --- Mode switching ---

    @on(Button.Pressed, "#switch-btn")
    def _on_switch(self) -> None:
        if self._mode == "qr":
            self._switch_to_phone()
        else:
            self._switch_to_qr()

    def _switch_to_phone(self) -> None:
        self._mode = "phone"
        self._phone_step = 1
        self.query_one("#qr-display").add_class("hidden")
        self.query_one("#phone-input").remove_class("hidden")
        self.query_one("#code-input").add_class("hidden")
        self.query_one("#password-input").add_class("hidden")
        self.query_one("#action-btn").remove_class("hidden")
        self.query_one("#action-btn", Button).label = "Code senden"
        self.query_one("#action-btn", Button).disabled = False
        self.query_one("#subtitle", Static).update(
            "Telefonnummer eingeben (z.B. +49...)"
        )
        self.query_one("#switch-btn", Button).label = "Mit QR-Code anmelden"
        self.query_one("#error-msg", Static).update("")
        self.query_one("#phone-input", Input).focus()

    def _switch_to_qr(self) -> None:
        self._mode = "qr"
        self.query_one("#phone-input").add_class("hidden")
        self.query_one("#code-input").add_class("hidden")
        self.query_one("#password-input").add_class("hidden")
        self.query_one("#action-btn").add_class("hidden")
        self.query_one("#qr-display").remove_class("hidden")
        self.query_one("#subtitle", Static).update(
            "QR-Code mit Telegram-App scannen"
        )
        self.query_one("#switch-btn", Button).label = "Mit Telefonnummer anmelden"
        self.query_one("#error-msg", Static).update("")
        self._start_qr_login()

    # --- QR code login ---

    @work()
    async def _start_qr_login(self) -> None:
        error = self.query_one("#error-msg", Static)
        qr_display = self.query_one("#qr-display", Static)

        try:
            self._qr_login = await self.app.telegram_service.qr_login()
            qr_text = _render_qr(self._qr_login.url)
            qr_display.update(qr_text)
        except Exception as e:
            error.update(f"QR-Login Fehler: {e}")
            return

        try:
            await self._qr_login.wait()
            self.dismiss(True)
        except SessionPasswordNeededError:
            self._show_2fa_for_qr()
        except Exception as e:
            error.update(f"QR-Login Fehler: {e}")

    def _show_2fa_for_qr(self) -> None:
        self._mode = "2fa_qr"
        self.query_one("#qr-display").add_class("hidden")
        self.query_one("#password-input").remove_class("hidden")
        self.query_one("#action-btn").remove_class("hidden")
        self.query_one("#action-btn", Button).label = "Anmelden"
        self.query_one("#switch-btn").add_class("hidden")
        self.query_one("#subtitle", Static).update("2FA Passwort eingeben")
        self.query_one("#password-input", Input).focus()

    # --- Phone login ---

    @on(Button.Pressed, "#action-btn")
    def _on_action(self) -> None:
        if self._mode == "phone" and self._phone_step == 1:
            self._send_code()
        elif self._mode == "phone" and self._phone_step == 2:
            self._verify_code()
        elif self._phone_step == 3 or self._mode == "2fa_qr":
            self._verify_2fa()

    @on(Input.Submitted)
    def _on_submit(self) -> None:
        if self._mode != "qr":
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
            await self.app.telegram_service.send_code(phone)
            self._phone_step = 2
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
            self._phone_step = 3
            self.query_one("#code-input").add_class("hidden")
            self.query_one("#password-input").remove_class("hidden")
            self.query_one("#switch-btn").add_class("hidden")
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
