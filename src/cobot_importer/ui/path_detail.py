"""Detail panel for editing a path segment."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..core import PathPoint, PathSegment


class PathDetailWidget(QWidget):
    """Widget for editing properties of a single path segment."""

    path_updated = Signal(PathSegment)
    points_changed = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._path: Optional[PathSegment] = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._general_group = QGroupBox("通用参数")
        general_layout = QFormLayout(self._general_group)

        self._name_edit = QLineEdit()
        self._name_edit.editingFinished.connect(self._on_name_changed)
        general_layout.addRow("名称", self._name_edit)

        self._enabled_check = QCheckBox("启用该路径")
        self._enabled_check.stateChanged.connect(self._on_enabled_changed)
        general_layout.addRow("状态", self._enabled_check)

        self._speed_spin = self._create_spin(0.0, 2000.0, 10.0, 100.0)
        self._speed_spin.valueChanged.connect(self._on_speed_changed)
        general_layout.addRow("速度 (mm/s)", self._speed_spin)

        self._density_spin = self._create_spin(0.1, 10.0, 0.1, 1.0)
        self._density_spin.valueChanged.connect(self._on_density_changed)
        general_layout.addRow("走点密度 (mm)", self._density_spin)

        self._blend_spin = self._create_spin(0.0, 100.0, 1.0, 0.0)
        self._blend_spin.valueChanged.connect(self._on_blend_changed)
        general_layout.addRow("过渡半径 (mm)", self._blend_spin)

        self._approach_spin = self._create_spin(0.0, 200.0, 1.0, 10.0)
        self._approach_spin.valueChanged.connect(self._on_approach_changed)
        general_layout.addRow("接近高度 (mm)", self._approach_spin)

        self._retract_spin = self._create_spin(0.0, 200.0, 1.0, 10.0)
        self._retract_spin.valueChanged.connect(self._on_retract_changed)
        general_layout.addRow("离开高度 (mm)", self._retract_spin)

        layout.addWidget(self._general_group)

        self._points_group = QGroupBox("路径点")
        points_layout = QVBoxLayout(self._points_group)
        self._points_table = QTableWidget(0, 6)
        self._points_table.setHorizontalHeaderLabels(["X", "Y", "Z", "Rx", "Ry", "Rz"])
        self._points_table.horizontalHeader().setStretchLastSection(True)
        self._points_table.verticalHeader().setVisible(False)
        self._points_table.setEditTriggers(QTableWidget.AllEditTriggers)
        self._points_table.itemChanged.connect(self._on_point_edited)
        points_layout.addWidget(self._points_table)

        buttons_layout = QHBoxLayout()
        self._add_point_button = QPushButton("添加点位")
        self._add_point_button.clicked.connect(self._on_add_point)
        self._remove_point_button = QPushButton("删除选中点")
        self._remove_point_button.clicked.connect(self._on_remove_point)
        buttons_layout.addWidget(self._add_point_button)
        buttons_layout.addWidget(self._remove_point_button)
        points_layout.addLayout(buttons_layout)

        layout.addWidget(self._points_group)
        layout.addStretch(1)

    def _create_spin(self, minimum: float, maximum: float, step: float, default: float) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(minimum, maximum)
        spin.setSingleStep(step)
        spin.setDecimals(3)
        spin.setValue(default)
        spin.setKeyboardTracking(False)
        return spin

    def set_path(self, path: Optional[PathSegment]) -> None:
        self._path = path
        self._update_ui()

    def _update_ui(self) -> None:
        updating = getattr(self, "_updating", False)
        self._updating = True
        try:
            if self._path is None:
                self.setEnabled(False)
                self._points_table.setRowCount(0)
                return
            self.setEnabled(True)
            self._name_edit.setText(self._path.name)
            self._enabled_check.setChecked(self._path.enabled)
            self._speed_spin.setValue(self._path.speed)
            self._density_spin.setValue(self._path.point_density)
            self._blend_spin.setValue(self._path.blend_radius)
            self._approach_spin.setValue(self._path.approach_height)
            self._retract_spin.setValue(self._path.retract_height)
            self._points_table.blockSignals(True)
            self._points_table.setRowCount(len(self._path.points))
            for row, point in enumerate(self._path.points):
                values = [point.x, point.y, point.z, point.rx, point.ry, point.rz]
                for column, value in enumerate(values):
                    item = QTableWidgetItem(f"{value:.3f}")
                    item.setData(Qt.EditRole, float(value))
                    self._points_table.setItem(row, column, item)
            self._points_table.blockSignals(False)
        finally:
            self._updating = updating

    def _notify_update(self) -> None:
        if self._path is None:
            return
        self.path_updated.emit(self._path)

    def _on_name_changed(self) -> None:
        if not self._path or getattr(self, "_updating", False):
            return
        self._path.name = self._name_edit.text() or self._path.name
        self._notify_update()

    def _on_enabled_changed(self, state: int) -> None:
        if not self._path or getattr(self, "_updating", False):
            return
        self._path.enabled = state == Qt.Checked
        self._notify_update()

    def _on_speed_changed(self, value: float) -> None:
        if not self._path or getattr(self, "_updating", False):
            return
        self._path.speed = value
        self._notify_update()

    def _on_density_changed(self, value: float) -> None:
        if not self._path or getattr(self, "_updating", False):
            return
        self._path.point_density = value
        self._notify_update()

    def _on_blend_changed(self, value: float) -> None:
        if not self._path or getattr(self, "_updating", False):
            return
        self._path.blend_radius = value
        self._notify_update()

    def _on_approach_changed(self, value: float) -> None:
        if not self._path or getattr(self, "_updating", False):
            return
        self._path.approach_height = value
        self._notify_update()

    def _on_retract_changed(self, value: float) -> None:
        if not self._path or getattr(self, "_updating", False):
            return
        self._path.retract_height = value
        self._notify_update()

    def _on_add_point(self) -> None:
        if not self._path:
            return
        last = self._path.points[-1] if self._path.points else PathPoint(0, 0, 0)
        new_point = PathPoint(last.x, last.y, last.z)
        self._path.points.append(new_point)
        self._update_ui()
        self._notify_update()
        self.points_changed.emit()

    def _on_remove_point(self) -> None:
        if not self._path:
            return
        selected_rows = sorted({index.row() for index in self._points_table.selectedIndexes()}, reverse=True)
        for row in selected_rows:
            if 0 <= row < len(self._path.points):
                del self._path.points[row]
        self._update_ui()
        self._notify_update()
        if selected_rows:
            self.points_changed.emit()

    def _on_point_edited(self, item: QTableWidgetItem) -> None:
        if not self._path or getattr(self, "_updating", False):
            return
        row = item.row()
        column = item.column()
        if not (0 <= row < len(self._path.points)):
            return
        value = item.data(Qt.EditRole)
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return
        point = self._path.points[row]
        if column == 0:
            point.x = numeric
        elif column == 1:
            point.y = numeric
        elif column == 2:
            point.z = numeric
        elif column == 3:
            point.rx = numeric
        elif column == 4:
            point.ry = numeric
        elif column == 5:
            point.rz = numeric
        self._notify_update()
        self.points_changed.emit()
