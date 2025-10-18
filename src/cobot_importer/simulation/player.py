"""Animate path traversal for visual verification."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List

import numpy as np

from ..core import PathPoint, PathSegment


@dataclass
class PathFrame:
    position: np.ndarray
    segment_index: int
    point_index: int


class PathPlayer:
    """Generate interpolated frames across project paths."""

    def __init__(self, segments: Iterable[PathSegment], resolution: float = 1.0) -> None:
        self._segments = list(segments)
        self._resolution = max(resolution, 0.1)
        self._frames: List[PathFrame] = []
        self._prepare_frames()

    def _prepare_frames(self) -> None:
        frames: List[PathFrame] = []
        for s_index, segment in enumerate(self._segments):
            if not segment.enabled or len(segment.points) < 2:
                continue
            for p_index in range(len(segment.points) - 1):
                start = self._point_to_array(segment.points[p_index])
                end = self._point_to_array(segment.points[p_index + 1])
                steps = max(int(np.linalg.norm(end - start) / self._resolution), 1)
                for step in range(steps):
                    t = step / steps
                    position = start * (1 - t) + end * t
                    frames.append(PathFrame(position=position, segment_index=s_index, point_index=p_index))
        self._frames = frames

    def iter_frames(self) -> Iterable[PathFrame]:
        return iter(self._frames)

    @staticmethod
    def _point_to_array(point: PathPoint) -> np.ndarray:
        return np.array([point.x, point.y, point.z], dtype=float)
