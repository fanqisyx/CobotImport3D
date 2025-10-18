"""Discover and load exporter plugins from the plugins directory."""

from __future__ import annotations

import importlib.util
import logging
from pathlib import Path
from typing import Dict, List, Optional

from .base import RobotProgramExporter

logger = logging.getLogger(__name__)


class PluginLoader:
    """Loads exporter plugins from a configurable directory."""

    def __init__(self, plugin_directory: str | Path | None = None) -> None:
        self._directory = Path(plugin_directory or Path.cwd() / "plugins")
        self._exporters: Dict[str, RobotProgramExporter] = {}

    @property
    def directory(self) -> Path:
        return self._directory

    def discover(self) -> None:
        self._exporters.clear()
        if not self._directory.exists():
            logger.warning("Plugin directory does not exist: %s", self._directory)
            return

        for file in self._directory.glob("*.py"):
            exporter = self._load_from_file(file)
            if exporter:
                self._exporters[exporter.id] = exporter

    def get_exporters(self) -> List[RobotProgramExporter]:
        return list(self._exporters.values())

    def get(self, exporter_id: str) -> Optional[RobotProgramExporter]:
        return self._exporters.get(exporter_id)

    def _load_from_file(self, path: Path) -> Optional[RobotProgramExporter]:
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if spec is None or spec.loader is None:
            logger.error("Failed to create spec for plugin %s", path)
            return None
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)  # type: ignore[assignment]
        except Exception as exc:  # pragma: no cover - best effort logging
            logger.exception("Failed to load plugin %s: %s", path, exc)
            return None

        exporter = getattr(module, "EXPORTER", None)
        if exporter is None or not isinstance(exporter, RobotProgramExporter):
            logger.warning("No valid EXPORTER found in %s", path.name)
            return None
        logger.info("Loaded exporter plugin: %s", exporter.display_name)
        return exporter
