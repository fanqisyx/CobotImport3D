"""Domain models for project, paths, and events."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Optional, Dict, Any


class IOType(str, Enum):
    """Types of IO bindings supported by path segments."""

    DIGITAL_OUTPUT = "digital_output"
    DIGITAL_INPUT = "digital_input"
    ANALOG_OUTPUT = "analog_output"
    NETWORK_COMMAND = "network_command"


@dataclass
class IOEvent:
    """Represents an IO or communication event triggered at a path waypoint."""

    io_type: IOType
    identifier: str
    value: Optional[float] = None
    payload: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["io_type"] = self.io_type.value
        return data

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "IOEvent":
        return IOEvent(
            io_type=IOType(data.get("io_type", IOType.DIGITAL_OUTPUT)),
            identifier=data.get("identifier", ""),
            value=data.get("value"),
            payload=data.get("payload"),
        )


@dataclass
class PathPoint:
    """A single waypoint along a path."""

    x: float
    y: float
    z: float
    rx: float = 0.0
    ry: float = 0.0
    rz: float = 0.0
    io_events: List[IOEvent] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "rx": self.rx,
            "ry": self.ry,
            "rz": self.rz,
            "io_events": [event.to_dict() for event in self.io_events],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "PathPoint":
        return PathPoint(
            x=data.get("x", 0.0),
            y=data.get("y", 0.0),
            z=data.get("z", 0.0),
            rx=data.get("rx", 0.0),
            ry=data.get("ry", 0.0),
            rz=data.get("rz", 0.0),
            io_events=[IOEvent.from_dict(evt) for evt in data.get("io_events", [])],
        )


@dataclass
class PathSegment:
    """A user-defined path over the workpiece."""

    name: str
    points: List[PathPoint] = field(default_factory=list)
    speed: float = 100.0
    point_density: float = 1.0
    blend_radius: float = 0.0
    retract_height: float = 10.0
    approach_height: float = 10.0
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "points": [point.to_dict() for point in self.points],
            "speed": self.speed,
            "point_density": self.point_density,
            "blend_radius": self.blend_radius,
            "retract_height": self.retract_height,
            "approach_height": self.approach_height,
            "enabled": self.enabled,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "PathSegment":
        return PathSegment(
            name=data.get("name", "Path"),
            points=[PathPoint.from_dict(point) for point in data.get("points", [])],
            speed=data.get("speed", 100.0),
            point_density=data.get("point_density", 1.0),
            blend_radius=data.get("blend_radius", 0.0),
            retract_height=data.get("retract_height", 10.0),
            approach_height=data.get("approach_height", 10.0),
            enabled=data.get("enabled", True),
        )


@dataclass
class Project:
    """Represents an entire planning project."""

    name: str = "New Project"
    model_path: Optional[str] = None
    model_transform: List[List[float]] = field(
        default_factory=lambda: [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )
    paths: List[PathSegment] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "model_path": self.model_path,
            "model_transform": self.model_transform,
            "paths": [path.to_dict() for path in self.paths],
            "metadata": self.metadata,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Project":
        return Project(
            name=data.get("name", "New Project"),
            model_path=data.get("model_path"),
            model_transform=data.get("model_transform")
            or [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ],
            paths=[PathSegment.from_dict(path) for path in data.get("paths", [])],
            metadata=data.get("metadata", {}),
        )

    def ensure_path(self, index: int) -> PathSegment:
        try:
            return self.paths[index]
        except IndexError as exc:
            raise ValueError(f"Path index {index} is out of range") from exc

    def add_path(self, segment: Optional[PathSegment] = None) -> PathSegment:
        segment = segment or PathSegment(name=f"Path {len(self.paths) + 1}")
        self.paths.append(segment)
        return segment

    def remove_path(self, index: int) -> None:
        self.ensure_path(index)
        del self.paths[index]

    def clone_path(self, index: int) -> PathSegment:
        path = self.ensure_path(index)
        cloned = PathSegment.from_dict(path.to_dict())
        cloned.name = f"{path.name} Copy"
        self.paths.insert(index + 1, cloned)
        return cloned
