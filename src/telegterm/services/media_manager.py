"""Media download, cache and thumbnail generation."""

from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path

from PIL import Image

from telegterm.models.config import MEDIA_CACHE_DIR, AVATAR_CACHE_DIR


class MediaManager:
    def __init__(self) -> None:
        MEDIA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        AVATAR_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def get_cached(self, media_id: str) -> Path | None:
        for ext in (".jpg", ".png", ".webp"):
            path = MEDIA_CACHE_DIR / f"{media_id}{ext}"
            if path.exists():
                return path
        return None

    def get_thumb_path(self, media_id: str) -> Path:
        return MEDIA_CACHE_DIR / f"thumb_{media_id}.jpg"

    def get_avatar_path(self, entity_id: int) -> Path:
        return AVATAR_CACHE_DIR / f"{entity_id}.jpg"

    async def create_thumbnail(
        self, source: str | Path, media_id: str, size: tuple[int, int] = (200, 200)
    ) -> Path:
        thumb_path = self.get_thumb_path(media_id)
        if thumb_path.exists():
            return thumb_path

        def _generate():
            img = Image.open(source)
            img.thumbnail(size)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(str(thumb_path), "JPEG", quality=80)

        await asyncio.to_thread(_generate)
        return thumb_path

    async def create_pdf_thumbnail(
        self, pdf_path: str | Path, media_id: str
    ) -> Path | None:
        thumb_path = self.get_thumb_path(media_id)
        if thumb_path.exists():
            return thumb_path

        def _generate():
            try:
                from pdf2image import convert_from_path
                images = convert_from_path(str(pdf_path), first_page=1, last_page=1, size=(200, None))
                if images:
                    img = images[0]
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    img.save(str(thumb_path), "JPEG", quality=80)
                    return True
            except Exception:
                return False
            return False

        success = await asyncio.to_thread(_generate)
        return thumb_path if success else None

    async def create_video_thumbnail(
        self, video_path: str | Path, media_id: str
    ) -> Path | None:
        thumb_path = self.get_thumb_path(media_id)
        if thumb_path.exists():
            return thumb_path

        def _generate():
            try:
                result = subprocess.run(
                    [
                        "ffmpeg", "-i", str(video_path),
                        "-vframes", "1", "-an",
                        "-s", "200x200",
                        "-ss", "0",
                        str(thumb_path),
                        "-y",
                    ],
                    capture_output=True,
                    timeout=10,
                )
                return result.returncode == 0
            except (FileNotFoundError, subprocess.TimeoutExpired):
                return False

        success = await asyncio.to_thread(_generate)
        return thumb_path if success else None

    async def convert_sticker(
        self, webp_path: str | Path, media_id: str
    ) -> Path:
        png_path = MEDIA_CACHE_DIR / f"sticker_{media_id}.png"
        if png_path.exists():
            return png_path

        def _convert():
            img = Image.open(webp_path)
            img.save(str(png_path), "PNG")

        await asyncio.to_thread(_convert)
        return png_path

    def cleanup(self, max_age_days: int = 30) -> int:
        import time
        now = time.time()
        removed = 0
        for path in MEDIA_CACHE_DIR.iterdir():
            if path.is_file():
                age_days = (now - path.stat().st_mtime) / 86400
                if age_days > max_age_days:
                    path.unlink()
                    removed += 1
        return removed
