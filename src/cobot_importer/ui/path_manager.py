"""Composite widget managing path list and details."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..core import PathSegment, Project
from .path_detail import PathDetailWidget


class PathManagerWidget(QWidget):
    """Handles listing and editing project paths."""

    path_selection_changed = Signal(int)
    project_modified = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._list_widget = QListWidget()
        self._list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self._list_widget.currentRowChanged.connect(self._on_row_changed)
        self._list_widget.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self._list_widget, stretch=2)

        buttons_layout = QHBoxLayout()
        self._add_button = QPushButton("添加路径")
        self._add_button.clicked.connect(self._on_add_path)
        self._remove_button = QPushButton("删除路径")
        self._remove_button.clicked.connect(self._on_remove_path)
        self._copy_button = QPushButton("复制路径")
        self._copy_button.clicked.connect(self._on_copy_path)
        buttons_layout.addWidget(self._add_button)
        buttons_layout.addWidget(self._remove_button)
        buttons_layout.addWidget(self._copy_button)
        layout.addLayout(buttons_layout)

        self._detail_widget = PathDetailWidget()
        self._detail_widget.path_updated.connect(self._on_path_updated)
        self._detail_widget.points_changed.connect(self.project_modified)
        layout.addWidget(self._detail_widget, stretch=3)

        self._project: Optional[Project] = None

    def set_project(self, project: Project) -> None:
        self._project = project
        self._reload_list()

    def current_segment(self) -> Optional[PathSegment]:
        if not self._project:
            return None
        row = self._list_widget.currentRow()
        if row < 0 or row >= len(self._project.paths):
            return None
        return self._project.paths[row]

    def _reload_list(self) -> None:
        self._list_widget.blockSignals(True)
        self._list_widget.clear()
        if not self._project:
            self._detail_widget.set_path(None)
            self._list_widget.blockSignals(False)
            return
        for path in self._project.paths:
            item = QListWidgetItem(path.name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)
            item.setCheckState(Qt.Checked if path.enabled else Qt.Unchecked)
            self._list_widget.addItem(item)
        self._list_widget.blockSignals(False)
        if self._project.paths:
            self._list_widget.setCurrentRow(0)
        else:
            self._detail_widget.set_path(None)

    def _on_row_changed(self, row: int) -> None:
        if not self._project or row < 0 or row >= len(self._project.paths):
            self._detail_widget.set_path(None)
            return
        self._detail_widget.set_path(self._project.paths[row])
        self.path_selection_changed.emit(row)

    def _on_item_changed(self, item: QListWidgetItem) -> None:
        if not self._project:
            return
        row = self._list_widget.row(item)
        if not (0 <= row < len(self._project.paths)):
            return
        segment = self._project.paths[row]
        segment.enabled = item.checkState() == Qt.Checked
        segment.name = item.text()
        self.project_modified.emit()

    def _on_add_path(self) -> None:
        if not self._project:
            return
        segment = self._project.add_path()
        self._reload_list()
        row = self._project.paths.index(segment)
        self._list_widget.setCurrentRow(row)
        self.project_modified.emit()

    def _on_remove_path(self) -> None:
        if not self._project:
            return
        row = self._list_widget.currentRow()
        if row < 0:
            return
        self._project.remove_path(row)
        self._reload_list()
        self.project_modified.emit()

    def _on_copy_path(self) -> None:
        if not self._project:
            return
        row = self._list_widget.currentRow()
        if row < 0:
            return
        self._project.clone_path(row)
        self._reload_list()
        self._list_widget.setCurrentRow(row + 1)
        self.project_modified.emit()

    def _on_path_updated(self, segment: PathSegment) -> None:
        row = self._list_widget.currentRow()
        if row >= 0:
            item = self._list_widget.item(row)
            item.setText(segment.name)
            item.setCheckState(Qt.Checked if segment.enabled else Qt.Unchecked)
        self.project_modified.emit()
