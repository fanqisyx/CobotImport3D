"""3D scene view leveraging pyqtgraph's OpenGL widget."""

from __future__ import annotations

from typing import Dict, Optional

import numpy as np
from PySide6.QtWidgets import QVBoxLayout, QWidget
import pyqtgraph.opengl as gl

from ..core import MeshGeometry, Project


class SceneView(QWidget):
    """Displays the workpiece mesh and planned paths."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._view = gl.GLViewWidget()
        self._view.opts["distance"] = 800
        self._view.setBackgroundColor((30, 30, 30))
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._view)

        self._grid = gl.GLGridItem()
        self._grid.scale(50, 50, 1)
        self._view.addItem(self._grid)

        self._mesh_item: Optional[gl.GLMeshItem] = None
        self._path_items: Dict[str, gl.GLLinePlotItem] = {}
        self._marker = gl.GLScatterPlotItem(size=10, color=(1, 0, 0, 1))
        self._view.addItem(self._marker)
        self._marker.setData(pos=np.array([[0, 0, 0]]))
        self._marker.hide()

    def set_mesh(self, geometry: Optional[MeshGeometry]) -> None:
        if self._mesh_item is not None:
            self._view.removeItem(self._mesh_item)
            self._mesh_item = None
        if geometry is None:
            return
        mesh_data = gl.MeshData(vertexes=geometry.vertices, faces=geometry.faces)
        self._mesh_item = gl.GLMeshItem(meshdata=mesh_data, smooth=True, drawEdges=False, color=(0.6, 0.6, 0.8, 1.0))
        self._mesh_item.setGLOptions("opaque")
        self._view.addItem(self._mesh_item)

    def clear_paths(self) -> None:
        for item in self._path_items.values():
            self._view.removeItem(item)
        self._path_items.clear()

    def update_paths(self, project: Project) -> None:
        self.clear_paths()
        for index, segment in enumerate(project.paths):
            if not segment.enabled or len(segment.points) < 2:
                continue
            points = np.array([[p.x, p.y, p.z] for p in segment.points])
            color = (0.2 + 0.6 * (index % 3) / 3.0, 0.8, 0.4 + 0.4 * (index % 5) / 5.0, 1.0)
            item = gl.GLLinePlotItem(pos=points, width=2, antialias=True, color=color, mode="line_strip")
            self._view.addItem(item)
            self._path_items[segment.name] = item

    def show_simulation_marker(self, position: Optional[np.ndarray]) -> None:
        if position is None:
            self._marker.setData(pos=np.array([[0, 0, 0]]))
            self._marker.hide()
        else:
            self._marker.setData(pos=np.array([position]))
            self._marker.show()

    def reset_camera(self) -> None:
        self._view.opts["azimuth"] = 45
        self._view.opts["elevation"] = 30
        self._view.opts["distance"] = 800
