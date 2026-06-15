import os
from typing import Iterable


def ensure_directory(path: str) -> None:
    """Ensure that a directory exists."""
    os.makedirs(path, exist_ok=True)


def resolve_export_path(filename: str) -> str:
    """Resolve a safe export path inside the exports folder."""
    export_dir = os.path.join(os.path.dirname(__file__), "..", "exports")
    ensure_directory(export_dir)
    return os.path.join(export_dir, filename)


def resolve_upload_path(filename: str) -> str:
    """Resolve a safe upload or placeholder path inside uploads."""
    upload_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
    ensure_directory(upload_dir)
    return os.path.join(upload_dir, filename)


def save_text_report(path: str, content: str) -> None:
    """Write a text report to a file."""
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)


def get_supported_csv_extensions() -> list[str]:
    """Supported upload file extensions."""
    return [".csv", ".xlsx", ".xls", ".json", ".sql"]


def is_valid_file_path(file_path: str) -> bool:
    """Validate that an incoming file path is a string and uses allowed extension."""
    if not isinstance(file_path, str) or not file_path:
        return False
    extension = os.path.splitext(file_path)[1].lower()
    return extension in get_supported_csv_extensions()
