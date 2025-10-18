"""Mesh loading utilities supporting STL and STEP formats."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import trimesh

logger = logging.getLogger(__name__)


@dataclass
class MeshGeometry:
    """Container for mesh data for rendering."""

    vertices: np.ndarray
    faces: np.ndarray
    normals: Optional[np.ndarray]


class ModelLoader:
    """Load mesh files and provide data for rendering."""

    SUPPORTED_EXTENSIONS = {".stl", ".step", ".stp", ".obj"}

    @staticmethod
    def load_mesh(path: str | Path) -> MeshGeometry:
        filepath = Path(path)
        if not filepath.exists():
            raise FileNotFoundError(f"Model file not found: {filepath}")
        if filepath.suffix.lower() not in ModelLoader.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported model format '{filepath.suffix}'. Supported: {sorted(ModelLoader.SUPPORTED_EXTENSIONS)}"
            )

        logger.info("Loading mesh: %s", filepath)
        mesh = trimesh.load_mesh(filepath, force='mesh')
        if mesh.is_empty:
            raise ValueError("Loaded mesh is empty")

        if not isinstance(mesh, trimesh.Trimesh):
            mesh = mesh.as_trimesh()

        vertices = np.array(mesh.vertices, dtype=float)
        faces = np.array(mesh.faces, dtype=int)
        normals = np.array(mesh.vertex_normals, dtype=float) if mesh.vertex_normals is not None else None
        return MeshGeometry(vertices=vertices, faces=faces, normals=normals)
