"""
Helpers to persist uploaded images and generate thumbnails.
"""

from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Optional, Tuple
from uuid import uuid4

from PIL import Image, UnidentifiedImageError

from ..config import settings


class ImageStorageError(RuntimeError):
    """Raised when an uploaded image cannot be persisted."""


def save_image_and_thumbnail(
    data: bytes, original_filename: Optional[str]
) -> Tuple[Optional[str], str]:
    """
    Persist only a downsized JPEG thumbnail for the provided image.

    Args:
        data: Raw image bytes
        original_filename: Optional filename (used to detect extension for validation)

    Returns:
        Tuple (original_relative_path, thumbnail_relative_path). The original path
        is always ``None`` because full-resolution files are discarded after thumbnail
        generation.
    """

    base_dir = _get_media_root()
    unique_id = uuid4().hex
    date_path = datetime.utcnow().strftime("%Y/%m/%d")

    thumbnail_rel = (
        Path(settings.media_thumbnails_subdir) / date_path / f"{unique_id}.jpg"
    )
    thumbnail_path = base_dir / thumbnail_rel

    _write_thumbnail(thumbnail_path, data)
    return None, thumbnail_rel.as_posix()


def _get_media_root() -> Path:
    media_root = Path(settings.media_root).expanduser()
    media_root.mkdir(parents=True, exist_ok=True)
    return media_root


def _write_thumbnail(path: Path, data: bytes) -> None:
    """Generate and persist a JPEG thumbnail."""

    try:
        image = Image.open(BytesIO(data))
    except UnidentifiedImageError as exc:
        raise ImageStorageError("Unable to decode uploaded image") from exc

    with image:
        thumb = image.convert("RGB")
        thumb.thumbnail((settings.thumbnail_max_size, settings.thumbnail_max_size))
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            thumb.save(path, format="JPEG", optimize=True, quality=85)
        except OSError as exc:
            raise ImageStorageError("Unable to save thumbnail image") from exc
