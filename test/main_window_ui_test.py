import os

import pytest

pytest.importorskip("numpy")
pytest.importorskip("pandas")
pytest.importorskip("PIL")
pytest.importorskip("PySide6")

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QPushButton

from src.main_window import ElidedLabel, MainWindow
from src.tag import TagModel
from src.tag.panel import TagManagerDialog


@pytest.fixture(scope="module", autouse=True)
def qt_application():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def main_window():
    window = MainWindow()
    yield window
    window.close()
    window.deleteLater()


def test_main_window_exposes_themed_workspace_structure(main_window):
    assert main_window.objectName() == "mainWindow"
    assert main_window.windowTitle() == "文件管理器"
    assert main_window.view.objectName() == "fileTable"
    assert main_window.tag_panel.objectName() == "tagPanel"
    assert main_window.layout_widget.findChild(QLabel, "emptyState") is main_window.empty_state

    headers = [
        main_window.viewmodel.headerData(
            column,
            Qt.Orientation.Horizontal,
            Qt.ItemDataRole.DisplayRole,
        )
        for column in range(5)
    ]
    assert headers == ["文件名", "预览", "Tag", "相对路径", "绝对路径"]
    assert main_window.view.alternatingRowColors()
    assert not main_window.view.showGrid()


def test_main_window_actions_and_empty_status_are_ready(main_window):
    buttons = {button.text(): button for button in main_window.findChildren(QPushButton)}
    assert "test button" not in buttons
    assert buttons["添加文件"].objectName() == "primaryButton"
    assert {"设置预览图", "设置标签", "打开所在文件夹", "打开文件"} <= buttons.keys()

    menu_titles = [action.text() for action in main_window.menu_bar.actions()]
    assert menu_titles == ["文件", "Tag"]
    file_actions = main_window.menu_bar.actions()[0].menu().actions()
    assert sum(action.isSeparator() for action in file_actions) == 2

    assert main_window.table_stack.currentWidget() is main_window.empty_state
    assert "添加文件" in main_window.empty_state.text()
    assert main_window.status_count_label.text() == "显示 0 / 共 0"
    assert isinstance(main_window.work_dir_label, ElidedLabel)
    assert main_window.work_dir_label.toolTip() == main_window.work_dir_label.fullText


def test_tag_manager_action_states_follow_tree_selection():
    tag_model = TagModel()
    group = tag_model.add_group("文件类型", "file-type")
    tag_model.add_tag("图片", group.id)
    dialog = TagManagerDialog(tag_model)
    try:
        assert not dialog.action_buttons["rename"].isEnabled()
        assert not dialog.action_buttons["move"].isEnabled()
        assert not dialog.action_buttons["delete"].isEnabled()

        exclusive_root = dialog.tree.topLevelItem(0)
        group_item = exclusive_root.child(0)
        dialog.tree.setCurrentItem(group_item)
        assert dialog.action_buttons["rename"].isEnabled()
        assert not dialog.action_buttons["move"].isEnabled()
        assert dialog.action_buttons["delete"].isEnabled()

        dialog.tree.setCurrentItem(group_item.child(0))
        assert dialog.action_buttons["rename"].isEnabled()
        assert dialog.action_buttons["move"].isEnabled()
        assert dialog.action_buttons["delete"].isEnabled()
    finally:
        dialog.close()
        dialog.deleteLater()
