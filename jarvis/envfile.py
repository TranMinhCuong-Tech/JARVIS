from __future__ import annotations

import os

from .platform_utils import app_dir

# A plain ".env" filename would collide with this project's existing ".env/"
# virtualenv folder, so a distinct name is used instead.
_ENV_FILENAMES = ("jarvis.env",)


def load_env_file() -> None:
    """Load KEY=VALUE pairs from a project-local file into os.environ.

    Exporting variables in one terminal and then launching JARVIS from a
    different terminal, an IDE run configuration, or a desktop shortcut is a
    very common way for SPOTIFY_CLIENT_ID / SPOTIFY_CLIENT_SECRET to silently
    never reach the process, even though the user "did set them". A
    project-local file removes that footgun entirely. Real environment
    variables, if already present, always take priority and are never
    overwritten here.
    """
    for filename in _ENV_FILENAMES:
        path = app_dir() / filename
        if not path.exists():
            continue
        try:
            for raw_line in path.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
        except Exception:
            pass
