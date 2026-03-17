"""Search screen -- search chats and messages."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static, Input, ListView, ListItem
from textual.containers import Vertical, Center
from textual import on, work
from rich.text import Text


class SearchResult(ListItem):
    def __init__(self, title: str, preview: str, chat_id: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.chat_id = chat_id
        self._title = title
        self._preview = preview

    def compose(self) -> ComposeResult:
        text = Text()
        text.append(self._title, style="bold")
        text.append(f"  {self._preview}", style="dim")
        yield Static(text)


class SearchScreen(ModalScreen[int | None]):
    CSS = """
    SearchScreen {
        align: center middle;
    }
    SearchScreen #search-container {
        width: 60;
        height: 20;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }
    SearchScreen Input {
        margin-bottom: 1;
    }
    SearchScreen ListView {
        height: 1fr;
        background: $background;
    }
    """

    def __init__(self, chat_id: int | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._chat_id = chat_id

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="search-container"):
                yield Input(
                    placeholder="Suchen...",
                    id="search-input",
                )
                yield ListView(id="results")

    def on_mount(self) -> None:
        self.query_one("#search-input", Input).focus()

    @on(Input.Changed, "#search-input")
    def _on_search_changed(self, event: Input.Changed) -> None:
        query = event.value.strip()
        if len(query) >= 2:
            self._do_search(query)

    @work()
    async def _do_search(self, query: str) -> None:
        results = self.query_one("#results", ListView)
        results.clear()

        if self._chat_id:
            messages = await self.app.telegram_service.search_messages(
                self._chat_id, query, limit=20
            )
            for msg in messages:
                preview = msg.text[:50] if msg.text else ""
                results.append(SearchResult(
                    title=msg.sender_name,
                    preview=preview,
                    chat_id=msg.chat_id,
                ))
        else:
            chats = await self.app.telegram_service.get_dialogs(limit=50)
            for chat in chats:
                if query.lower() in chat.title.lower():
                    results.append(SearchResult(
                        title=chat.title,
                        preview=chat.preview_text,
                        chat_id=chat.id,
                    ))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if isinstance(event.item, SearchResult):
            self.dismiss(event.item.chat_id)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)
