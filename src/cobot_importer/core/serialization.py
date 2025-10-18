"""Utilities for serializing and loading project files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .project import Project


class ProjectSerializer:
    """Serialize project data to and from JSON files."""

    FILE_EXTENSION = ".cobot3d"

    @staticmethod
    def load(path: str | Path) -> Project:
        with open(path, "r", encoding="utf-8") as handle:
            data: Any = json.load(handle)
        return Project.from_dict(data)

    @staticmethod
    def save(project: Project, path: str | Path) -> None:
        payload = project.to_dict()
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)

    @staticmethod
    def suggest_path(project: Project, directory: str | Path) -> Path:
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        filename = f"{project.name.replace(' ', '_').lower()}{ProjectSerializer.FILE_EXTENSION}"
        return directory / filename
