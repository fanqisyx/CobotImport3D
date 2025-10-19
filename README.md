# Cobot Importer 3D

该项目基于随仓库提供的需求文档，实现了一套**模块化、可扩展**的协作机械臂三维路径规划与仿真工具原型。主要特点：

- 使用 Python + PySide6 构建跨平台桌面界面，方便在 Win10/Win11 系统上部署；
- 支持 STL/STEP/OBJ 等常见三维模型导入，基于 `trimesh` 解析；
- 可视化路径编辑：右侧面板提供路径段列表与参数调节、点位表格编辑；
- 简单仿真：利用插值算法在三维视图中预览路径执行；
- 插件化导出体系：默认内置 URScript 导出器，同时支持从 `plugins/` 目录加载额外导出插件；
- 项目数据以 JSON (`.cobot3d`) 格式保存，便于版本管理与团队协作。

## 环境准备

```bash
python -m venv .venv
source .venv/bin/activate  # Windows 使用 .venv\Scripts\activate
pip install -e .
```

若首次安装 `PySide6`、`pyqtgraph` 时出现网络限制，可提前准备对应的离线轮子文件后通过 `pip install <wheel>` 安装。

## 运行

```bash
python -m cobot_importer.app
```

或直接使用 `cobot-importer` 可执行入口。

也可以在项目根目录下双击或运行 `start.py`，该脚本会自动将本地 `src/` 加入 `PYTHONPATH` 并启动图形界面，实现“一键启动”。

## 主要工作流

1. **新建或打开项目**：菜单栏 → 文件。
2. **导入工件模型**：支持 STL/STEP/STP/OBJ。
3. **编辑路径**：
   - 右侧列表管理路径段（添加/复制/删除、启用状态）。
   - 在“路径点”表格中录入或调整点位坐标、姿态。
4. **仿真验证**：菜单栏 → 仿真 → 开始仿真，在 3D 视图中查看执行轨迹与末端示踪点。
5. **导出机器人程序**：菜单栏 → 文件 → 导出机器人程序，选择导出器与保存位置。

## 插件扩展

- 插件目录默认为 `<项目根>/plugins/`，每个插件文件需定义 `EXPORTER` 变量并实现 `RobotProgramExporter` 协议。
- 可参考 `src/cobot_importer/plugins/builtin.py` 中的 `URScriptExporter` 实现。

## 测试

目前包含核心数据模型的序列化单元测试示例，可运行：

```bash
pytest
```

如需扩展测试，请在 `tests/` 目录下补充。
