"""
Unit tests for image metadata extraction and storage helpers.
"""

import os
import sys
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image, PngImagePlugin

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("JWT_SECRET_KEY", "testsecret")
os.environ.setdefault("API_KEYS", '["test_key"]')

from src.api.config import settings
from src.api.services.image_metadata import extract_png_metadata, MetadataExtractionError
from src.api.services.image_storage import ImageStorageError, save_image_and_thumbnail


def _build_png(parameters: str) -> bytes:
    """Create an in-memory PNG that mimics Stable Diffusion output."""
    image = Image.new("RGB", (32, 32), color="red")
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("parameters", parameters)
    buffer = BytesIO()
    image.save(buffer, format="PNG", pnginfo=metadata)
    return buffer.getvalue()


def test_extract_png_metadata_parses_prompts():
    data = _build_png(
        "masterpiece, ultra detail\nNegative prompt: bad, ugly\nSteps: 20, Seed: 12345"
    )
    metadata = extract_png_metadata(data)

    assert metadata.positive_prompt.startswith("masterpiece")
    assert metadata.negative_prompt == "bad, ugly"
    assert metadata.settings["Steps"] == "20"
    assert metadata.settings["Seed"] == "12345"


def test_extract_png_metadata_without_chunk_raises():
    image = Image.new("RGB", (16, 16), color="blue")
    buffer = BytesIO()
    image.save(buffer, format="PNG")

    with pytest.raises(MetadataExtractionError):
        extract_png_metadata(buffer.getvalue())


def test_save_image_and_thumbnail_persists_files(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "media_root", str(tmp_path / "media"))
    data = _build_png("prompt\nNegative prompt: none\nSteps: 10, Seed: 1")

    image_rel, thumb_rel = save_image_and_thumbnail(data, "sample.png")

    thumbnail = Path(settings.media_root) / thumb_rel

    assert image_rel is None
    assert thumbnail.exists()


def test_save_image_and_thumbnail_cleans_up_on_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "media_root", str(tmp_path / "media"))
    media_dir = Path(settings.media_root)

    with pytest.raises(ImageStorageError):
        save_image_and_thumbnail(b"not-a-png", "broken.png")

    thumbnails_dir = media_dir / settings.media_thumbnails_subdir

    if thumbnails_dir.exists():
        assert not any(p.is_file() for p in thumbnails_dir.rglob("*"))
