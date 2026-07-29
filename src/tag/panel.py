from __future__ import annotations

from typing import Iterable

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .schema import TagFilter, TagModel, normalize_tags


_KIND_ROLE = Qt.ItemDataRole.UserRole
_ID_ROLE = Qt.ItemDataRole.UserRole + 1


def _clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        child_layout = item.layout()
        widget = item.widget()
        if child_layout is not None:
            _clear_layout(child_layout)
        if widget is not None:
            widget.deleteLater()


class TagPanel(QFrame):
    filterChanged = Signal(object, object)
    clearFilterRequested = Signal()
    fileTagChanged = Signal(str, bool)
    manageRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tag_model = TagModel()
        self._tag_filter = TagFilter()
        self._current_file_name: str | None = None
        self._current_file_tags: list[str] = []
        self._updating = False
        self._filter_groups: dict[str, QButtonGroup] = {}
        self._filter_coexist: dict[str, QCheckBox] = {}
        self._file_groups: dict[str, QButtonGroup] = {}
        self._file_coexist: dict[str, QCheckBox] = {}

        self.setObjectName("tagPanel")
        self.setMinimumWidth(280)
        self.setMaximumWidth(420)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self._build_ui()
        self._apply_style()
        self.rebuild()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(12)

        header = QHBoxLayout()
        title_block = QVBoxLayout()
        title = QLabel("Tag 工作区")
        title.setObjectName("tagPanelTitle")
        subtitle = QLabel("筛选与当前文件标签")
        subtitle.setObjectName("tagPanelSubtitle")
        title_block.addWidget(title)
        title_block.addWidget(subtitle)
        header.addLayout(title_block)
        header.addStretch()
        manage_button = QPushButton("管理")
        manage_button.setObjectName("primaryButton")
        manage_button.clicked.connect(self.manageRequested.emit)
        header.addWidget(manage_button)
        root.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll_body = QWidget()
        scroll_layout = QVBoxLayout(scroll_body)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(12)

        filter_card = QFrame()
        filter_card.setObjectName("tagCard")
        filter_layout = QVBoxLayout(filter_card)
        filter_layout.setContentsMargins(12, 12, 12, 12)
        filter_header = QHBoxLayout()
        filter_title = QLabel("文件筛选")
        filter_title.setObjectName("sectionTitle")
        self.count_label = QLabel("0 / 0")
        self.count_label.setObjectName("countBadge")
        clear_button = QPushButton("清除")
        clear_button.setObjectName("quietButton")
        clear_button.clicked.connect(self._clear_filter)
        filter_header.addWidget(filter_title)
        filter_header.addStretch()
        filter_header.addWidget(self.count_label)
        filter_header.addWidget(clear_button)
        filter_layout.addLayout(filter_header)
        self.filter_content = QWidget()
        self.filter_content_layout = QVBoxLayout(self.filter_content)
        self.filter_content_layout.setContentsMargins(0, 4, 0, 0)
        self.filter_content_layout.setSpacing(8)
        filter_layout.addWidget(self.filter_content)
        scroll_layout.addWidget(filter_card)

        file_card = QFrame()
        file_card.setObjectName("tagCard")
        file_layout = QVBoxLayout(file_card)
        file_layout.setContentsMargins(12, 12, 12, 12)
        file_title = QLabel("当前文件")
        file_title.setObjectName("sectionTitle")
        self.current_file_label = QLabel("未选择文件")
        self.current_file_label.setObjectName("currentFileLabel")
        self.current_file_label.setWordWrap(True)
        file_layout.addWidget(file_title)
        file_layout.addWidget(self.current_file_label)
        self.file_content = QWidget()
        self.file_content_layout = QVBoxLayout(self.file_content)
        self.file_content_layout.setContentsMargins(0, 4, 0, 0)
        self.file_content_layout.setSpacing(8)
        file_layout.addWidget(self.file_content)
        scroll_layout.addWidget(file_card)
        scroll_layout.addStretch()

        scroll.setWidget(scroll_body)
        root.addWidget(scroll)

    def _apply_style(self):
        self.setStyleSheet("""
            QFrame#tagPanel {
                background: #F4F7FB;
                border-left: 1px solid #D9E2EF;
                color: #172033;
                font-family: "Noto Sans", "Microsoft YaHei UI";
                font-size: 13px;
            }
            QLabel#tagPanelTitle { font-size: 20px; font-weight: 600; color: #172033; }
            QLabel#tagPanelSubtitle { color: #64748B; font-size: 12px; }
            QFrame#tagCard {
                background: #FFFFFF;
                border: 1px solid #DDE6F2;
                border-radius: 10px;
            }
            QLabel#sectionTitle { font-size: 15px; font-weight: 600; color: #172033; }
            QLabel#currentFileLabel {
                color: #526078;
                background: #EAF0F8;
                border-radius: 6px;
                padding: 7px;
            }
            QLabel#countBadge {
                color: #1D4ED8;
                background: #DBEAFE;
                border-radius: 8px;
                padding: 2px 7px;
                font-weight: 600;
            }
            QPushButton {
                min-height: 26px;
                padding: 2px 10px;
                border-radius: 6px;
                border: 1px solid #CBD7E6;
                background: #FFFFFF;
                color: #172033;
            }
            QPushButton:hover { background: #EAF0F8; border-color: #94A9C4; }
            QPushButton#primaryButton {
                color: #FFFFFF;
                background: #2563EB;
                border-color: #2563EB;
                font-weight: 600;
            }
            QPushButton#primaryButton:hover { background: #1D4ED8; }
            QPushButton#quietButton { color: #526078; background: transparent; }
            QGroupBox {
                margin-top: 10px;
                padding-top: 8px;
                border: 1px solid #E1E8F2;
                border-radius: 7px;
                font-weight: 600;
                color: #526078;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }
            QCheckBox, QRadioButton { spacing: 7px; color: #172033; font-weight: 400; }
            QCheckBox:hover, QRadioButton:hover { color: #1D4ED8; }
            QScrollArea { background: transparent; }
        """)

    def setState(
        self,
        tag_model: TagModel,
        tag_filter: TagFilter,
        file_name: str | None,
        file_tags: Iterable[str] | None,
        visible_count: int,
        total_count: int,
    ):
        self._tag_model = tag_model
        self._tag_filter = tag_filter
        self._current_file_name = file_name
        self._current_file_tags = normalize_tags(file_tags)
        self.setCounts(visible_count, total_count)
        self.rebuild()

    def setSchema(self, tag_model: TagModel, tag_filter: TagFilter | None = None):
        self._tag_model = tag_model
        if tag_filter is not None:
            self._tag_filter = tag_filter
        self.rebuild()

    def setCurrentFile(self, name: str | None, tags: Iterable[str] | None = None):
        self._current_file_name = name
        self._current_file_tags = normalize_tags(tags)
        self._rebuild_file_editor()

    def setCounts(self, visible: int, total: int):
        self.count_label.setText(f"{visible} / {total}")

    def rebuild(self):
        self._updating = True
        try:
            self._rebuild_filter_editor()
            self._rebuild_file_editor()
        finally:
            self._updating = False

    def _make_group_box(self, title: str, parent_layout) -> tuple[QGroupBox, QVBoxLayout]:
        box = QGroupBox(title)
        layout = QVBoxLayout(box)
        layout.setContentsMargins(9, 10, 9, 8)
        layout.setSpacing(5)
        parent_layout.addWidget(box)
        return box, layout

    def _rebuild_filter_editor(self):
        _clear_layout(self.filter_content_layout)
        self._filter_groups.clear()
        self._filter_coexist.clear()

        for group in self._tag_model.exclusive_groups:
            _, layout = self._make_group_box(group.name, self.filter_content_layout)
            buttons = QButtonGroup(self)
            buttons.setExclusive(True)
            unrestricted = QRadioButton("不限")
            unrestricted.setProperty("tagValue", None)
            unrestricted.setChecked(group.id not in self._tag_filter.exclusive)
            buttons.addButton(unrestricted)
            layout.addWidget(unrestricted)
            for tag in group.tags:
                button = QRadioButton(tag)
                button.setProperty("tagValue", tag)
                button.setChecked(self._tag_filter.exclusive.get(group.id) == tag)
                buttons.addButton(button)
                layout.addWidget(button)
            buttons.buttonToggled.connect(self._on_filter_control_changed)
            self._filter_groups[group.id] = buttons

        if self._tag_model.coexist_tags:
            _, layout = self._make_group_box("共存 Tag", self.filter_content_layout)
            selected = set(self._tag_filter.coexist)
            for tag in self._tag_model.coexist_tags:
                checkbox = QCheckBox(tag)
                checkbox.setChecked(tag in selected)
                checkbox.toggled.connect(self._on_filter_control_changed)
                layout.addWidget(checkbox)
                self._filter_coexist[tag] = checkbox

        if not self._tag_model.all_tags:
            empty = QLabel("尚未定义 Tag，请点击“管理”创建。")
            empty.setWordWrap(True)
            empty.setStyleSheet("color: #64748B; padding: 8px 2px;")
            self.filter_content_layout.addWidget(empty)
        self.filter_content_layout.addStretch()

    def _rebuild_file_editor(self):
        _clear_layout(self.file_content_layout)
        self._file_groups.clear()
        self._file_coexist.clear()
        has_file = self._current_file_name is not None
        self.current_file_label.setText(self._current_file_name or "未选择文件")
        selected_tags = set(self._current_file_tags)

        for group in self._tag_model.exclusive_groups:
            _, layout = self._make_group_box(group.name, self.file_content_layout)
            buttons = QButtonGroup(self)
            buttons.setExclusive(True)
            selected_in_group = next((tag for tag in group.tags if tag in selected_tags), None)
            none_button = QRadioButton("未设置")
            none_button.setProperty("tagValue", None)
            none_button.setProperty("previousTag", selected_in_group)
            none_button.setChecked(selected_in_group is None)
            buttons.addButton(none_button)
            layout.addWidget(none_button)
            for tag in group.tags:
                button = QRadioButton(tag)
                button.setProperty("tagValue", tag)
                button.setChecked(tag == selected_in_group)
                buttons.addButton(button)
                layout.addWidget(button)
            buttons.buttonToggled.connect(self._on_file_group_changed)
            self._file_groups[group.id] = buttons

        if self._tag_model.coexist_tags:
            _, layout = self._make_group_box("共存 Tag", self.file_content_layout)
            for tag in self._tag_model.coexist_tags:
                checkbox = QCheckBox(tag)
                checkbox.setChecked(tag in selected_tags)
                checkbox.toggled.connect(
                    lambda checked, value=tag: self._on_file_tag_changed(value, checked)
                )
                layout.addWidget(checkbox)
                self._file_coexist[tag] = checkbox

        if not self._tag_model.all_tags:
            empty = QLabel("请先在 Tag 管理中创建标签。")
            empty.setStyleSheet("color: #64748B; padding: 8px 2px;")
            empty.setWordWrap(True)
            self.file_content_layout.addWidget(empty)
        self.file_content.setEnabled(has_file)
        self.file_content_layout.addStretch()

    def _collect_filter(self) -> tuple[dict[str, str], list[str]]:
        exclusive: dict[str, str] = {}
        for group_id, buttons in self._filter_groups.items():
            checked = buttons.checkedButton()
            if checked is not None and checked.property("tagValue"):
                exclusive[group_id] = checked.property("tagValue")
        coexist = [
            tag for tag, checkbox in self._filter_coexist.items()
            if checkbox.isChecked()
        ]
        return exclusive, coexist

    def _on_filter_control_changed(self, *args):
        if self._updating:
            return
        if len(args) == 2 and args[1] is False:
            return
        exclusive, coexist = self._collect_filter()
        self.filterChanged.emit(exclusive, coexist)

    def _clear_filter(self):
        if self._updating:
            return
        self.clearFilterRequested.emit()

    def _on_file_group_changed(self, button, checked: bool):
        if self._updating or not checked or self._current_file_name is None:
            return
        tag = button.property("tagValue")
        if tag:
            self.fileTagChanged.emit(tag, True)
        else:
            previous = button.property("previousTag")
            if previous:
                self.fileTagChanged.emit(previous, False)

    def _on_file_tag_changed(self, tag: str, checked: bool):
        if self._updating or self._current_file_name is None:
            return
        self.fileTagChanged.emit(tag, checked)


class TagManagerDialog(QDialog):
    operationRequested = Signal(str, object)

    def __init__(self, tag_model: TagModel, parent=None):
        super().__init__(parent)
        self._tag_model = tag_model
        self.setWindowTitle("Tag 管理")
        self.resize(620, 480)
        self._build_ui()
        self._apply_style()
        self.setTagModel(tag_model)

    def _build_ui(self):
        root = QVBoxLayout(self)
        title = QLabel("Tag 与互斥规则")
        title.setObjectName("dialogTitle")
        description = QLabel("互斥组内每个文件只能选择一个 Tag；共存 Tag 可以多选。")
        description.setObjectName("dialogDescription")
        root.addWidget(title)
        root.addWidget(description)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["名称", "类型"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setRootIsDecorated(True)
        self.tree.setColumnWidth(0, 360)
        root.addWidget(self.tree)

        actions = QHBoxLayout()
        for text, slot, object_name in [
            ("新增互斥组", self._add_group, "primaryButton"),
            ("新增 Tag", self._add_tag, "primaryButton"),
            ("改名", self._rename_selected, ""),
            ("移动 Tag", self._move_selected, ""),
            ("删除", self._delete_selected, "dangerButton"),
        ]:
            button = QPushButton(text)
            if object_name:
                button.setObjectName(object_name)
            button.clicked.connect(slot)
            actions.addWidget(button)
        actions.addStretch()
        root.addLayout(actions)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    def _apply_style(self):
        self.setStyleSheet("""
            QDialog { background: #F4F7FB; color: #172033; font-family: "Noto Sans", "Microsoft YaHei UI"; font-size: 13px; }
            QLabel#dialogTitle { font-size: 20px; font-weight: 600; color: #172033; }
            QLabel#dialogDescription { color: #526078; padding-bottom: 8px; }
            QTreeWidget { background: #FFFFFF; border: 1px solid #D9E2EF; border-radius: 8px; alternate-background-color: #F7F9FC; }
            QTreeWidget::item { min-height: 28px; }
            QTreeWidget::item:selected { background: #DBEAFE; color: #1D4ED8; }
            QPushButton { min-height: 28px; padding: 2px 12px; border: 1px solid #CBD7E6; border-radius: 6px; background: #FFFFFF; }
            QPushButton:hover { background: #EAF0F8; }
            QPushButton#primaryButton { color: #FFFFFF; background: #2563EB; border-color: #2563EB; }
            QPushButton#primaryButton:hover { background: #1D4ED8; }
            QPushButton#dangerButton { color: #C93C37; border-color: #E5B4B1; }
            QPushButton#dangerButton:hover { background: #FFF0EF; }
        """)

    def setTagModel(self, tag_model: TagModel):
        self._tag_model = tag_model
        self.tree.clear()

        exclusive_root = QTreeWidgetItem(["互斥组", "规则分类"])
        exclusive_root.setData(0, _KIND_ROLE, "exclusive_root")
        self.tree.addTopLevelItem(exclusive_root)
        for group in tag_model.exclusive_groups:
            group_item = QTreeWidgetItem([group.name, "互斥组"])
            group_item.setData(0, _KIND_ROLE, "group")
            group_item.setData(0, _ID_ROLE, group.id)
            exclusive_root.addChild(group_item)
            for tag in group.tags:
                tag_item = QTreeWidgetItem([tag, "互斥 Tag"])
                tag_item.setData(0, _KIND_ROLE, "tag")
                tag_item.setData(0, _ID_ROLE, tag)
                group_item.addChild(tag_item)

        coexist_root = QTreeWidgetItem(["共存 Tag", "规则分类"])
        coexist_root.setData(0, _KIND_ROLE, "coexist_root")
        self.tree.addTopLevelItem(coexist_root)
        for tag in tag_model.coexist_tags:
            tag_item = QTreeWidgetItem([tag, "共存 Tag"])
            tag_item.setData(0, _KIND_ROLE, "tag")
            tag_item.setData(0, _ID_ROLE, tag)
            coexist_root.addChild(tag_item)

        self.tree.expandAll()

    def _selected(self) -> tuple[str | None, object | None]:
        item = self.tree.currentItem()
        if item is None:
            return None, None
        return item.data(0, _KIND_ROLE), item.data(0, _ID_ROLE)

    def _destination_group_id(self, item: QTreeWidgetItem | None) -> str | None:
        while item is not None:
            kind = item.data(0, _KIND_ROLE)
            if kind == "group":
                return item.data(0, _ID_ROLE)
            if kind == "coexist_root":
                return None
            item = item.parent()
        return None

    def _add_group(self):
        name, ok = QInputDialog.getText(self, "新增互斥组", "组名")
        if ok and name.strip():
            self.operationRequested.emit("add_group", (name,))

    def _add_tag(self):
        selected = self.tree.currentItem()
        group_id = self._destination_group_id(selected)
        name, ok = QInputDialog.getText(self, "新增 Tag", "Tag 名称")
        if ok and name.strip():
            self.operationRequested.emit("add_tag", (name, group_id))

    def _rename_selected(self):
        kind, value = self._selected()
        if kind not in {"group", "tag"}:
            return
        current = self.tree.currentItem().text(0)
        name, ok = QInputDialog.getText(self, "改名", "新名称", text=current)
        if not ok or not name.strip() or name.strip() == current:
            return
        action = "rename_group" if kind == "group" else "rename_tag"
        self.operationRequested.emit(action, (value, name))

    def _delete_selected(self):
        kind, value = self._selected()
        if kind not in {"group", "tag"}:
            return
        label = self.tree.currentItem().text(0)
        if kind == "group":
            detail = "删除互斥组后，组内 Tag 会转为共存 Tag，不会从文件中删除。"
            action = "delete_group"
        else:
            detail = "删除 Tag 会同时移除所有文件对该 Tag 的引用。"
            action = "delete_tag"
        answer = QMessageBox.question(
            self,
            "确认删除",
            f"确定删除“{label}”吗？\n\n{detail}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.operationRequested.emit(action, (value,))

    def _move_selected(self):
        kind, tag = self._selected()
        if kind != "tag":
            return
        labels = ["共存 Tag"] + [group.name for group in self._tag_model.exclusive_groups]
        destination, ok = QInputDialog.getItem(
            self,
            "移动 Tag",
            "目标分类",
            labels,
            editable=False,
        )
        if not ok:
            return
        group_id = None
        if destination != "共存 Tag":
            group_id = next(
                group.id for group in self._tag_model.exclusive_groups
                if group.name == destination
            )
        self.operationRequested.emit("move_tag", (tag, group_id))
