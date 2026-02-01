import os
import shutil
from pathlib import Path
from urllib.parse import unquote

UPLOAD_DIR = "/home/steve/uploads"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def ensure_upload_dir():
    """Ensure the upload directory exists."""
    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


def sanitize_path(path_str):
    """
    Sanitize and validate a file path.
    Prevents directory traversal attacks.
    Returns the sanitized path or None if invalid.
    """
    if not path_str:
        return ""

    # URL decode the path
    try:
        path_str = unquote(path_str)
    except Exception:
        return None

    # Remove any leading/trailing slashes and normalize
    path_str = path_str.strip("/")

    # Prevent directory traversal
    if ".." in path_str or path_str.startswith("/"):
        return None

    # Split and filter out empty parts
    parts = [p for p in path_str.split("/") if p]

    # Validate each part (no special characters that could cause issues)
    for part in parts:
        if not part or part in (".", "..") or "/" in part or "\\" in part:
            return None

    return "/".join(parts)


def get_full_path(relative_path=""):
    """
    Get the full filesystem path for a relative path.
    Returns None if path is invalid.
    """
    sanitized = sanitize_path(relative_path)
    if sanitized is None:
        return None

    full_path = os.path.join(UPLOAD_DIR, sanitized)

    # Ensure the path is within UPLOAD_DIR (prevent directory traversal)
    full_path = os.path.normpath(full_path)
    if not full_path.startswith(os.path.normpath(UPLOAD_DIR)):
        return None

    return full_path


def is_safe_filename(filename):
    """Check if filename is safe (no path separators or special chars)."""
    if not filename:
        return False
    return "/" not in filename and "\\" not in filename and ".." not in filename


# Initialize upload directory on module import
ensure_upload_dir()

