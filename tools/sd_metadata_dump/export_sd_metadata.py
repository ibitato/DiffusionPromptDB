#!/usr/bin/env python3
"""
Standalone utility to export Stable Diffusion metadata from PNG files.

The script understands the `parameters` text chunk that AUTOMATIC1111 and
StabilityMatrix embed in generated images.  It extracts the positive prompt,
negative prompt, and the remaining execution settings for every PNG file under
the provided directory and writes them to either JSONL or CSV.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import struct
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator, Optional

META_LINE_RE = re.compile(r"^[A-Za-z0-9 _/+().-]+: ")


@dataclass
class ImageMetadata:
    """Holds extracted Stable Diffusion metadata for a single PNG file."""

    relative_path: str
    positive_prompt: str
    negative_prompt: str
    settings: Dict[str, str]
    raw_parameters: str


def iter_png_files(root: Path) -> Iterator[Path]:
    """Yield every PNG file below ``root``."""

    for path in sorted(root.rglob("*.png")):
        if path.is_file():
            yield path


def extract_parameters_chunk(path: Path) -> Optional[str]:
    """Return the text stored in the PNG ``parameters`` chunk, if present."""

    try:
        data = path.read_bytes()
    except OSError as exc:
        print(f"[warn] Cannot read {path}: {exc}", file=sys.stderr)
        return None

    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None

    pos = 8
    while pos + 8 <= len(data):
        length = int.from_bytes(data[pos : pos + 4], "big")
        chunk_type = data[pos + 4 : pos + 8].decode("ascii", errors="ignore")
        chunk_data = data[pos + 8 : pos + 8 + length]
        pos += 12 + length

        if chunk_type == "tEXt":
            keyword, text = chunk_data.split(b"\x00", 1)
            if keyword.decode("latin1") == "parameters":
                return text.decode("utf-8", errors="replace")
        elif chunk_type == "zTXt":
            keyword, rest = chunk_data.split(b"\x00", 1)
            if keyword.decode("latin1") != "parameters":
                continue
            if not rest:
                continue
            compressed = rest[1:]  # skip compression method byte
            try:
                text = zlib.decompress(compressed)
            except zlib.error as exc:
                print(f"[warn] Could not decompress chunk in {path}: {exc}", file=sys.stderr)
                continue
            return text.decode("utf-8", errors="replace")
        elif chunk_type == "iTXt":
            text = _parse_itxt(chunk_data)
            if text is None:
                continue
            keyword, value = text
            if keyword == "parameters":
                return value
    return None


def _parse_itxt(data: bytes) -> Optional[tuple[str, str]]:
    """Parse an iTXt chunk into ``(keyword, text)``."""

    try:
        keyword, rest = data.split(b"\x00", 1)
    except ValueError:
        return None

    if len(rest) < 2:
        return None

    compression_flag = rest[0]
    compression_method = rest[1]
    remainder = rest[2:]

    try:
        language_tag, remainder = remainder.split(b"\x00", 1)
        translated_keyword, text = remainder.split(b"\x00", 1)
    except ValueError:
        return None

    _ = language_tag  # not used
    _ = translated_keyword

    if compression_flag:
        try:
            text = zlib.decompress(text)
        except zlib.error:
            return None

    try:
        decoded_keyword = keyword.decode("latin1")
        decoded_text = text.decode("utf-8", errors="replace")
    except UnicodeDecodeError:
        return None

    return decoded_keyword, decoded_text


def parse_parameters_blob(blob: str) -> ImageMetadata:
    """Split the Stable Diffusion blob into prompts and settings."""

    positive_lines = []
    negative_lines = []
    info_lines = []
    state = "positive"

    for line in blob.splitlines():
        if state == "positive":
            if line.startswith("Negative prompt:"):
                negative_lines.append(line[len("Negative prompt:") :].strip())
                state = "negative"
            elif META_LINE_RE.match(line):
                info_lines.append(line)
                state = "info"
            else:
                positive_lines.append(line)
        elif state == "negative":
            if META_LINE_RE.match(line):
                info_lines.append(line)
                state = "info"
            elif line.startswith("Negative prompt:"):
                negative_lines.append(line[len("Negative prompt:") :].strip())
            else:
                negative_lines.append(line)
        else:
            info_lines.append(line)

    settings = parse_settings_lines(info_lines)

    return ImageMetadata(
        relative_path="",
        positive_prompt="\n".join(filter(None, (line.strip() for line in positive_lines))),
        negative_prompt="\n".join(filter(None, (line.strip() for line in negative_lines))),
        settings=settings,
        raw_parameters=blob,
    )


def parse_settings_lines(lines: Iterable[str]) -> Dict[str, str]:
    """Parse comma-separated ``key: value`` pairs from the tail lines."""

    if not lines:
        return {}

    flattened = ", ".join(line.strip() for line in lines if line.strip())
    segments = re.split(r",\s*", flattened)
    settings: Dict[str, str] = {}
    last_key: Optional[str] = None

    for segment in segments:
        if not segment:
            continue
        if ": " in segment:
            key, value = segment.split(": ", 1)
            settings[key.strip()] = value.strip()
            last_key = key.strip()
        elif last_key:
            settings[last_key] = f"{settings[last_key]}, {segment.strip()}"

    return settings


def build_records(root: Path) -> Iterator[ImageMetadata]:
    """Yield structured metadata for every PNG file containing SD data."""

    for path in iter_png_files(root):
        blob = extract_parameters_chunk(path)
        if not blob:
            continue
        record = parse_parameters_blob(blob)
        record.relative_path = str(path.relative_to(root))
        yield record


def export_jsonl(records: Iterable[ImageMetadata], destination: Path) -> int:
    """Write the metadata in JSON Lines format."""

    count = 0
    with destination.open("w", encoding="utf-8") as handle:
        for record in records:
            json.dump(
                {
                    "relative_path": record.relative_path,
                    "positive_prompt": record.positive_prompt,
                    "negative_prompt": record.negative_prompt,
                    "settings": record.settings,
                    "raw_parameters": record.raw_parameters,
                },
                handle,
                ensure_ascii=False,
            )
            handle.write("\n")
            count += 1
    return count


def export_csv(records: Iterable[ImageMetadata], destination: Path) -> int:
    """Write the metadata in CSV format."""

    fieldnames = [
        "relative_path",
        "positive_prompt",
        "negative_prompt",
        "settings_json",
        "raw_parameters",
    ]

    count = 0
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "relative_path": record.relative_path,
                    "positive_prompt": record.positive_prompt,
                    "negative_prompt": record.negative_prompt,
                    "settings_json": json.dumps(record.settings, ensure_ascii=False),
                    "raw_parameters": record.raw_parameters,
                }
            )
            count += 1
    return count


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(
        description="Export Stable Diffusion prompts/settings from PNG files."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("/mnt/d/sd-matrix/Data/Images"),
        help="Directory that will be scanned recursively for PNG images.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("tools/sd_metadata_dump/output/metadata.jsonl"),
        help="Destination file. Parent directories are created automatically.",
    )
    parser.add_argument(
        "--format",
        choices=("jsonl", "csv"),
        default="jsonl",
        help="Output format (default: jsonl).",
    )
    return parser.parse_args()


def main() -> None:
    """Entrypoint for the CLI."""

    args = parse_args()
    source = args.source.expanduser()
    if not source.exists():
        print(f"[error] Source directory {source} does not exist.", file=sys.stderr)
        sys.exit(1)

    records = build_records(source)
    output_path = args.output.expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.format == "jsonl":
        count = export_jsonl(records, output_path)
    else:
        count = export_csv(records, output_path)

    print(f"[info] Exported metadata for {count} image(s) to {output_path}")


if __name__ == "__main__":
    main()
