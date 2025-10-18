"""Built-in exporter implementations."""

from __future__ import annotations

from pathlib import Path
from typing import List

from .base import ExportResult, RobotProgramExporter
from ..core import Project, PathSegment


class URScriptExporter:
    """Generate a simplified URScript program from project paths."""

    id = "builtin.urscript"
    display_name = "Universal Robots URScript"

    def supported_extensions(self) -> List[str]:
        return [".script"]

    def export(self, project: Project, destination: str) -> ExportResult:
        if not project.paths:
            return ExportResult(False, "项目中没有路径，无法导出。")

        path = Path(destination)
        if path.suffix.lower() not in self.supported_extensions():
            path = path.with_suffix(self.supported_extensions()[0])

        lines: List[str] = ["def cobot_program():"]
        lines.append("  set_digital_out(0, False)")
        for segment in project.paths:
            if not segment.enabled:
                continue
            lines.extend(self._emit_segment(segment))
        lines.append("  end")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines))
        return ExportResult(True, "URScript 程序导出成功", str(path))

    def _emit_segment(self, segment: PathSegment) -> List[str]:
        commands: List[str] = []
        commands.append(f"  # Segment: {segment.name}")
        if not segment.points:
            commands.append("  # (跳过 - 无点位)")
            return commands
        for point in segment.points:
            pose = [point.x / 1000.0, point.y / 1000.0, point.z / 1000.0, point.rx, point.ry, point.rz]
            commands.append(
                "  movej({pose}, a=1.2, v={speed})".format(
                    pose=str(pose), speed=max(segment.speed / 1000.0, 0.05)
                )
            )
        commands.append("  # retract")
        last = segment.points[-1]
        retract_pose = [
            last.x / 1000.0,
            last.y / 1000.0,
            (last.z + segment.retract_height) / 1000.0,
            last.rx,
            last.ry,
            last.rz,
        ]
        commands.append("  movej({pose}, a=1.2, v=0.1)".format(pose=str(retract_pose)))
        return commands


BUILTIN_EXPORTERS: List[RobotProgramExporter] = [URScriptExporter()]
