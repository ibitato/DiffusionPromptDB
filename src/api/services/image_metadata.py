"""
Utilities to read Stable Diffusion metadata embedded in PNG files.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Dict, Iterable, Iterator, Optional, Tuple
import zlib


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
META_LINE_RE = re.compile(r"^[A-Za-z0-9 _/+().-]+:\s")
TEXT_CHUNK_TYPES = {"tEXt", "zTXt", "iTXt"}


class MetadataExtractionError(RuntimeError):
    """Raised when PNG metadata cannot be extracted."""


@dataclass
class ExtractedMetadata:
    """Structured Stable Diffusion metadata parsed from a PNG image."""

    positive_prompt: str
    negative_prompt: str
    settings: Dict[str, str]
    raw_parameters: str


def extract_png_metadata(data: bytes) -> ExtractedMetadata:
    """
    Extract Stable Diffusion metadata embedded in a PNG byte stream.

    Args:
        data: Raw PNG bytes

    Returns:
        ExtractedMetadata with prompts and settings

    Raises:
        MetadataExtractionError: If the file is not a PNG or lacks metadata
    """
    if not data.startswith(PNG_SIGNATURE):
        raise MetadataExtractionError("Provided file is not a PNG image.")

    parameters_blob: Optional[str] = None
    for chunk_type, chunk_data in _iter_chunks(data):
        if chunk_type not in TEXT_CHUNK_TYPES:
            continue
        decoded = _decode_text_chunk(chunk_type, chunk_data)
        if not decoded:
            continue
        keyword, text = decoded
        if keyword == "parameters":
            parameters_blob = text
            break

    if not parameters_blob:
        raise MetadataExtractionError(
            "PNG does not include Stable Diffusion 'parameters' metadata."
        )

    return _parse_parameters_blob(parameters_blob)


def _iter_chunks(data: bytes) -> Iterator[Tuple[str, bytes]]:
    """Yield PNG chunk type and payload."""

    pos = len(PNG_SIGNATURE)
    data_len = len(data)
    while pos + 8 <= data_len:
        length = int.from_bytes(data[pos : pos + 4], "big")
        chunk_type = data[pos + 4 : pos + 8].decode("ascii", errors="ignore")
        chunk_data = data[pos + 8 : pos + 8 + length]
        pos += 12 + length
        yield chunk_type, chunk_data
        if chunk_type == "IEND":
            break


def _decode_text_chunk(chunk_type: str, chunk_data: bytes) -> Optional[Tuple[str, str]]:
    """Decode tEXt/zTXt/iTXt chunks into (keyword, text)."""

    try:
        if chunk_type == "tEXt":
            keyword, text = chunk_data.split(b"\x00", 1)
            return keyword.decode("latin1"), text.decode("utf-8", errors="replace")
        if chunk_type == "zTXt":
            keyword, rest = chunk_data.split(b"\x00", 1)
            if not rest:
                return None
            # Skip compression method byte (always 0 for deflate)
            compressed = rest[1:]
            text = zlib.decompress(compressed)
            return keyword.decode("latin1"), text.decode("utf-8", errors="replace")
        if chunk_type == "iTXt":
            keyword, rest = chunk_data.split(b"\x00", 1)
            if len(rest) < 2:
                return None
            compression_flag = rest[0]
            remainder = rest[2:]  # skip compression flag + method
            language_tag, remainder = remainder.split(b"\x00", 1)
            translated_keyword, text = remainder.split(b"\x00", 1)

            _ = language_tag  # Not used
            _ = translated_keyword

            if compression_flag == 1:
                text = zlib.decompress(text)

            return keyword.decode("latin1"), text.decode("utf-8", errors="replace")
    except (ValueError, UnicodeDecodeError, zlib.error):
        return None

    return None


def _parse_parameters_blob(blob: str) -> ExtractedMetadata:
    """Split the Stable Diffusion blob into prompts and settings."""

    positive_lines = []
    negative_lines = []
    info_lines = []
    section = "positive"

    for raw_line in blob.splitlines():
        line = raw_line.strip()
        if not line:
            # Preserve intentional blank separators inside prompts
            if section == "positive":
                positive_lines.append("")
            elif section == "negative":
                negative_lines.append("")
            continue

        if section == "positive":
            if line.startswith("Negative prompt:"):
                negative_lines.append(line[len("Negative prompt:") :].strip())
                section = "negative"
            elif META_LINE_RE.match(line):
                info_lines.append(line)
                section = "info"
            else:
                positive_lines.append(line)
        elif section == "negative":
            if line.startswith("Negative prompt:"):
                negative_lines.append(line[len("Negative prompt:") :].strip())
            elif META_LINE_RE.match(line):
                info_lines.append(line)
                section = "info"
            else:
                negative_lines.append(line)
        else:
            info_lines.append(line)

    settings = _parse_settings_lines(info_lines)
    positive_prompt = "\n".join(_trim_lines(positive_lines)).strip()
    negative_prompt = "\n".join(_trim_lines(negative_lines)).strip()

    return ExtractedMetadata(
        positive_prompt=positive_prompt,
        negative_prompt=negative_prompt,
        settings=settings,
        raw_parameters=blob,
    )


def _parse_settings_lines(lines: Iterable[str]) -> Dict[str, str]:
    """Parse comma-separated key/value pairs into a dictionary."""

    text = ", ".join(line.strip() for line in lines if line.strip())
    if not text:
        return {}

    segments = re.split(r",\s*", text)
    settings: Dict[str, str] = {}
    last_key: Optional[str] = None

    for segment in segments:
        if not segment:
            continue
        if ": " in segment:
            key, value = segment.split(": ", 1)
            key = key.strip()
            settings[key] = value.strip()
            last_key = key
        elif last_key:
            # Values containing commas (e.g. TI: "a, b")
            settings[last_key] = f"{settings[last_key]}, {segment.strip()}"

    return settings


def _trim_lines(lines: Iterable[str]) -> Iterator[str]:
    """Strip trailing spaces but keep intentional blank lines."""

    for line in lines:
        yield line.strip() if line else ""
