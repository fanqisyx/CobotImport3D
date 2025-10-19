#!/usr/bin/env python3
"""Convenience launcher for the Cobot Importer application."""

from __future__ import annotations

import sys
from pathlib import Path


def ensure_src_on_path() -> None:
    """Prepend the local ``src`` directory to ``sys.path`` if present."""

    project_root = Path(__file__).resolve().parent
    src_dir = project_root / "src"
    if src_dir.is_dir():
        sys.path.insert(0, str(src_dir))


def main() -> int:
    """Entry point used for one-click start of the GUI application."""

    ensure_src_on_path()

    from cobot_importer.app import main as app_main

    return app_main()


if __name__ == "__main__":
    sys.exit(main())
