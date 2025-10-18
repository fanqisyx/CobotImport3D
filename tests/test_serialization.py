from pathlib import Path

from cobot_importer.core import PathPoint, PathSegment, Project, ProjectSerializer


def test_project_roundtrip(tmp_path: Path) -> None:
    project = Project(name="Demo")
    segment = project.add_path(PathSegment(name="Seg1"))
    segment.points.extend(
        [
            PathPoint(0, 0, 0),
            PathPoint(10, 0, 0),
            PathPoint(10, 10, 0),
        ]
    )
    path = tmp_path / "project.cobot3d"
    ProjectSerializer.save(project, path)
    loaded = ProjectSerializer.load(path)
    assert loaded.name == project.name
    assert len(loaded.paths) == 1
    assert len(loaded.paths[0].points) == 3
