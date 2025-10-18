"""Base classes for robot program exporters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from ..core import Project


@dataclass
class ExportResult:
    """Result of running an exporter."""

    success: bool
    message: str
    output_path: str | None = None


@runtime_checkable
class RobotProgramExporter(Protocol):
    """Protocol for robot program exporters."""

    @property
    def id(self) -> str:
        ...

    @property
    def display_name(self) -> str:
        ...

    def supported_extensions(self) -> list[str]:
        ...

    def export(self, project: Project, destination: str) -> ExportResult:
        ...
