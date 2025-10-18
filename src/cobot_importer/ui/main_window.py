"""Main application window."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import numpy as np
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFileDialog,
    QInputDialog,
    QMainWindow,
    QMessageBox,
    QSplitter,
)

from ..core import ModelLoader, Project, ProjectSerializer
from ..plugins import PluginLoader
from ..plugins.builtin import BUILTIN_EXPORTERS
from ..simulation import PathPlayer
from .path_manager import PathManagerWidget
from .scene_view import SceneView

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Primary window orchestrating UI components."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Cobot Importer 3D")
        self.resize(1400, 900)

        self._project = Project()
        self._project_path: Optional[Path] = None
        self._mesh_geometry = None

        self._scene_view = SceneView()
        self._path_manager = PathManagerWidget()
        self._path_manager.set_project(self._project)
        self._path_manager.project_modified.connect(self._on_project_modified)

        splitter = QSplitter()
        splitter.addWidget(self._scene_view)
        splitter.addWidget(self._path_manager)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        self.setCentralWidget(splitter)

        self._plugin_loader = PluginLoader()
        self._exporters = {exporter.id: exporter for exporter in BUILTIN_EXPORTERS}
        self._load_plugins()

        self._simulation_timer = QTimer(self)
        self._simulation_timer.timeout.connect(self._advance_simulation)
        self._simulation_frames: List[np.ndarray] = []
        self._simulation_index = 0

        self._build_menu()
        self.statusBar().showMessage("准备就绪")

    # region Menu and actions
    def _build_menu(self) -> None:
        menu = self.menuBar()

        file_menu = menu.addMenu("文件(&F)")
        new_action = QAction("新建项目", self)
        new_action.triggered.connect(self._new_project)
        file_menu.addAction(new_action)

        open_action = QAction("打开项目...", self)
        open_action.triggered.connect(self._open_project)
        file_menu.addAction(open_action)

        save_action = QAction("保存", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_project)
        file_menu.addAction(save_action)

        save_as_action = QAction("另存为...", self)
        save_as_action.triggered.connect(self._save_project_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        import_action = QAction("导入3D模型...", self)
        import_action.triggered.connect(self._import_model)
        file_menu.addAction(import_action)

        export_action = QAction("导出机器人程序...", self)
        export_action.triggered.connect(self._export_robot_program)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = menu.addMenu("视图(&V)")
        reset_camera_action = QAction("重置相机", self)
        reset_camera_action.triggered.connect(self._scene_view.reset_camera)
        view_menu.addAction(reset_camera_action)

        simulation_menu = menu.addMenu("仿真(&S)")
        start_sim_action = QAction("开始仿真", self)
        start_sim_action.triggered.connect(self._start_simulation)
        simulation_menu.addAction(start_sim_action)

        stop_sim_action = QAction("停止仿真", self)
        stop_sim_action.triggered.connect(self._stop_simulation)
        simulation_menu.addAction(stop_sim_action)

    # endregion

    # region Project management
    def _new_project(self) -> None:
        if not self._confirm_discard_changes():
            return
        name, ok = QInputDialog.getText(self, "新建项目", "项目名称", text="New Project")
        if not ok:
            return
        self._project = Project(name=name or "New Project")
        self._project_path = None
        self._path_manager.set_project(self._project)
        self._scene_view.set_mesh(None)
        self._scene_view.clear_paths()
        self._on_project_modified()

    def _open_project(self) -> None:
        if not self._confirm_discard_changes():
            return
        path, _ = QFileDialog.getOpenFileName(
            self,
            "打开项目",
            str(Path.cwd()),
            "Cobot3D Project (*.cobot3d);;JSON (*.json)",
        )
        if not path:
            return
        try:
            project = ProjectSerializer.load(path)
        except Exception as exc:
            QMessageBox.critical(self, "打开失败", f"无法加载项目: {exc}")
            return
        self._project = project
        self._project_path = Path(path)
        self._path_manager.set_project(self._project)
        self._load_model_if_exists()
        self._on_project_modified()

    def _save_project(self) -> None:
        if self._project_path is None:
            self._save_project_as()
            return
        try:
            ProjectSerializer.save(self._project, self._project_path)
        except Exception as exc:
            QMessageBox.critical(self, "保存失败", f"写入项目文件失败: {exc}")
            return
        self.statusBar().showMessage("项目已保存", 3000)

    def _save_project_as(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "项目另存为",
            str(Path.cwd() / f"{self._project.name}.cobot3d"),
            "Cobot3D Project (*.cobot3d)",
        )
        if not path:
            return
        self._project_path = Path(path)
        self._save_project()

    def _confirm_discard_changes(self) -> bool:
        # This simplified version always allows; extend with change tracking.
        return True

    # endregion

    # region Model handling
    def _import_model(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "导入3D模型",
            str(Path.cwd()),
            "Mesh Files (*.stl *.step *.stp *.obj)",
        )
        if not path:
            return
        try:
            geometry = ModelLoader.load_mesh(path)
        except Exception as exc:
            QMessageBox.critical(self, "导入失败", f"无法加载模型: {exc}")
            logger.exception("Failed to load model")
            return
        self._mesh_geometry = geometry
        self._project.model_path = path
        self._scene_view.set_mesh(geometry)
        self._on_project_modified()

    def _load_model_if_exists(self) -> None:
        if self._project.model_path:
            try:
                geometry = ModelLoader.load_mesh(self._project.model_path)
            except Exception as exc:  # pragma: no cover - best effort
                QMessageBox.warning(self, "模型缺失", f"无法加载模型: {exc}")
                self._mesh_geometry = None
                self._scene_view.set_mesh(None)
                return
            self._mesh_geometry = geometry
            self._scene_view.set_mesh(geometry)
        else:
            self._scene_view.set_mesh(None)

    # endregion

    # region Export
    def _load_plugins(self) -> None:
        self._plugin_loader.discover()
        for exporter in self._plugin_loader.get_exporters():
            self._exporters[exporter.id] = exporter

    def _export_robot_program(self) -> None:
        if not self._exporters:
            QMessageBox.warning(self, "无导出插件", "未找到任何机器人程序导出器")
            return
        exporter_ids = list(self._exporters.keys())
        names = [self._exporters[eid].display_name for eid in exporter_ids]
        selected_name, ok = QInputDialog.getItem(
            self,
            "选择导出格式",
            "导出器",
            names,
            editable=False,
        )
        if not ok:
            return
        try:
            exporter_id = exporter_ids[names.index(selected_name)]
        except ValueError:
            QMessageBox.warning(self, "导出失败", "未能识别所选导出器")
            return
        exporter = self._exporters[exporter_id]
        path, _ = QFileDialog.getSaveFileName(
            self,
            "导出机器人程序",
            str(Path.cwd()),
            ";;".join(f"{exporter.display_name} (*{ext})" for ext in exporter.supported_extensions()),
        )
        if not path:
            return
        result = exporter.export(self._project, path)
        if result.success:
            self.statusBar().showMessage(result.message, 5000)
        else:
            QMessageBox.warning(self, "导出失败", result.message)

    # endregion

    # region Simulation
    def _start_simulation(self) -> None:
        player = PathPlayer(self._project.paths, resolution=5.0)
        frames = [frame.position for frame in player.iter_frames()]
        if not frames:
            QMessageBox.information(self, "仿真", "没有足够的路径点用于仿真")
            return
        self._simulation_frames = frames
        self._simulation_index = 0
        self._simulation_timer.start(30)
        self.statusBar().showMessage("仿真进行中...", 0)

    def _stop_simulation(self) -> None:
        self._simulation_timer.stop()
        self._scene_view.show_simulation_marker(None)
        self.statusBar().showMessage("仿真已停止", 3000)

    def _advance_simulation(self) -> None:
        if not self._simulation_frames:
            self._stop_simulation()
            return
        position = self._simulation_frames[self._simulation_index]
        self._scene_view.show_simulation_marker(position)
        self._simulation_index = (self._simulation_index + 1) % len(self._simulation_frames)

    # endregion

    def _on_project_modified(self) -> None:
        self._scene_view.update_paths(self._project)
        self.statusBar().showMessage("项目已更新", 1500)
