"""Full-screen media viewer."""

from __future__ import annotations

import subprocess
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.widgets import Static
from textual.containers import Vertical, Center


class MediaViewerScreen(ModalScreen[None]):
    CSS = """
    MediaViewerScreen {
        align: center middle;
        background: $background 90%;
    }
    MediaViewerScreen #viewer-container {
        width: 90%;
        height: 90%;
        border: thick $primary;
        background: $background;
    }
    MediaViewerScreen #media-info {
        dock: bottom;
        height: 1;
        background: $surface;
        padding: 0 1;
        color: $text-muted;
    }
    MediaViewerScreen #image-area {
        width: 100%;
        height: 1fr;
        content-align: center middle;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close", show=False),
        Binding("q", "close", "Close", show=False),
        Binding("s", "save", "Save", show=False),
    ]

    def __init__(self, media_path: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._media_path = media_path

    def compose(self) -> ComposeResult:
        with Vertical(id="viewer-container"):
            with Center(id="image-area"):
                try:
                    from textual_image.widget import Image
                    yield Image(self._media_path)
                except ImportError:
                    yield Static(f"[Bild: {self._media_path}]")
            yield Static(
                f"  {Path(self._media_path).name}  |  s: Speichern  q/Esc: Schliessen",
                id="media-info",
            )

    def action_close(self) -> None:
        self.dismiss(None)

    def action_save(self) -> None:
        downloads = Path.home() / "Downloads"
        downloads.mkdir(exist_ok=True)
        src = Path(self._media_path)
        dest = downloads / src.name
        if dest.exists():
            stem = src.stem
            suffix = src.suffix
            i = 1
            while dest.exists():
                dest = downloads / f"{stem}_{i}{suffix}"
                i += 1

        import shutil
        shutil.copy2(str(src), str(dest))
        self.notify(f"Gespeichert: {dest}")
