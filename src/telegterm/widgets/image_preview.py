"""Inline image preview widget using textual-image."""

from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static


class ImagePreview(Widget):
    DEFAULT_CSS = """
    ImagePreview {
        width: 100%;
        height: auto;
        max-height: 10;
        padding: 0 2;
    }
    """

    def __init__(self, image_path: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._image_path = image_path

    def compose(self) -> ComposeResult:
        if not Path(self._image_path).exists():
            yield Static(f"[Bild nicht gefunden: {self._image_path}]")
            return

        try:
            from textual_image.widget import Image
            yield Image(self._image_path)
        except ImportError:
            yield Static(f"[Bild: {Path(self._image_path).name}]")
