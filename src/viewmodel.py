import os

import pandas as pd

from PySide6.QtWidgets import (
    QWidget
)
from PySide6.QtGui import (
    QStandardItemModel, QStandardItem
)

from .vbao_wrapper import vbao
# import vbao
from .table_item import TableItem, TableItemChecklist
from .tag import (
    TagFilter, TagModel, TagRuleError, normalize_tag_name, normalize_tags
)
from .model import Model
from .row_mapping import source_index_for_view_row
from .vm_commands import *


class ViewModel(QStandardItemModel, vbao.core.ViewModel):
    """
    viewmodel存储从dataframe转化而来的信息
    item_list 存储总共的、用于保存的信息
    """

    # initialize
    def __init__(self, parent=None, ):
        super().__init__(parent)

        self.model = Model()
        self.tag_model = TagModel()
        self.tag_filter = TagFilter()
        self.setListener(vbao.DummyPropListener())

        self.registerCommands({
            "clear": CommandClear(self),
            "save": CommandSave(self),
            "load": CommandLoad(self),
            "add_file": CommandAddTableRow,
            "delete_rows": CommandDeleteRows,
            "update_image": CommandUpdatePreviewImage,
            "update_tags": CommandUpdateTags,
            "toggle_file_tag": CommandToggleFileTag,
            "manage_tags": CommandManageTagDefinition,
            "filter_tags": CommandFilterTags,
            "clear_filters": CommandClearTagFilters,
            "open": CommandOpenFile,
            "change_dir": CommandCD,
        })

    def init(self, start_load_path: str = ''):
        self.model.loadConfig()

        self.clear()
        self.setProperty_vbao("temp_dir", self.model.temp_dir)
        self.setProperty_vbao("save_format", self.model.save_format)
        self.setProperty_vbao("work_dir", os.getcwd())
        self.triggerPropertyNotifications("work_dir")
        if os.path.exists(start_load_path):
            self.loadData(start_load_path)

    def clear(self):
        self.tag_filter.clear()
        self.setProperty_vbao("filter_index", None)
        self.setProperty_vbao("visible_source_indices", [])
        self.setProperty_vbao("item_list", [])
        self.onDataChanged()
        self.triggerCommandNotifications("clear", True)

    # property
    @property
    def config(self):
        return self.model.config

    @property
    def work_dir(self):
        return self.getProperty("work_dir")

    @property
    def visible_source_indices(self) -> list[int]:
        indices = self.getProperty_vbao("visible_source_indices")
        return list(indices) if indices is not None else []

    def sourceIndexForViewRow(self, view_row: int) -> int:
        return source_index_for_view_row(self.visible_source_indices, view_row)

    def itemForViewRow(self, view_row: int) -> TableItem:
        source_index = self.sourceIndexForViewRow(view_row)
        return self.getProperty_vbao("item_list")[source_index]

    # save/load
    def loadData(self, filename):
        """Load file records and their optional Tag schema sidecar."""
        try:
            df = self.model.load(filename)
            items = TableItem.fromRecords(df)
            metadata = self.model.loadMetadata(filename)
            tag_model = TagModel.from_dict(metadata)

            for item in items:
                tag_model.register_existing_tags(item.tags)
            for item in items:
                item.setTags(tag_model.enforce_file_tags(item.tags))
                if self.config["auto_show_image_file"]:
                    item.autoDetectImage()
        except (OSError, UnicodeError, ValueError, TypeError, KeyError) as exc:
            self._notifyTagError(f"加载失败：{exc}")
            self.triggerCommandNotifications("load", False)
            return pd.DataFrame()

        self.tag_model = tag_model
        self.tag_filter.clear()
        self.setProperty_vbao('item_list', items)

        work_dir = metadata.get("work_dir")
        if isinstance(work_dir, str) and os.path.exists(work_dir):
            self.setProperty_vbao("work_dir", work_dir)
            self.triggerPropertyNotifications("work_dir")

        self.onDataChanged()
        self.triggerPropertyNotifications("tag_schema")
        self.triggerCommandNotifications("load", True)
        return df

    def _getWorkEnv(self):
        metadata = {"work_dir": self.work_dir}
        metadata.update(self.tag_model.to_dict())
        return metadata

    def saveData(self, filename):
        items = self.getProperty_vbao("item_list") or []
        try:
            sidecar_path = self.model.metadataPath(filename)
            if os.path.abspath(sidecar_path) == os.path.abspath("config.json"):
                raise ValueError("同名 JSON 会覆盖应用配置 config.json，请更换 CSV 文件名")

            for item in items:
                self.tag_model.register_existing_tags(item.tags)
                conflicts = self.tag_model.validate_file_tags(item.tags)
                if conflicts:
                    group_names = [
                        self.tag_model.get_group(group_id).name
                        for group_id in conflicts
                    ]
                    raise TagRuleError(
                        f"文件 {item.short_name} 的互斥 Tag 冲突：{', '.join(group_names)}"
                    )

            self.model.save(items, filename)
            self.model.saveMetadata(filename, self._getWorkEnv())
        except (OSError, UnicodeError, ValueError, TypeError, TagRuleError) as exc:
            self._notifyTagError(f"保存失败：{exc}")
            self.triggerCommandNotifications("save", False)
            return

        self.triggerPropertyNotifications("tag_schema")
        self.triggerCommandNotifications("save", True)

    def _calculateVisibleSourceIndices(self) -> list[int]:
        items = self.getProperty_vbao("item_list") or []
        if self.tag_filter.is_empty:
            return list(range(len(items)))
        return [
            source_index
            for source_index, item in enumerate(items)
            if self.tag_filter.matches(item.tags)
        ]

    def onDataChanged(self):
        items = self.getProperty_vbao("item_list") or []
        visible_indices = self._calculateVisibleSourceIndices()
        self.setProperty_vbao("visible_source_indices", visible_indices)
        self.setProperty_vbao(
            "filter_index",
            None if self.tag_filter.is_empty else visible_indices,
        )

        self.setRowCount(len(visible_indices))
        if items:
            col_count = items[0].expected_cols
            if self.columnCount() < col_count:
                self.setColumnCount(col_count)

        for view_row, source_index in enumerate(visible_indices):
            item: TableItem = items[source_index]
            self.addTableRow(view_row, item)

        self.triggerPropertyNotifications("items")

    def addTableRow(self, idx, item: TableItem):
        viewer = {'short_name': lambda: QStandardItem(item.short_name),
                  'short_name_icon': lambda: QStandardItem(item.icon, item.short_name),
                  'rela_path': lambda: QStandardItem(os.path.relpath(item.abs_path, self.work_dir)),
                  'abs_path': lambda: QStandardItem(item.abs_path),
                  'icon': lambda: QStandardItem(item.icon, ''),
                  'tags': lambda: QStandardItem(item.tags_text),
                  'empty': lambda: QStandardItem()
                  }

        for check in item.checklist:
            if check.role == TableItemChecklist.ModelRole:
                # immediately throw KeyError if not match
                fn = viewer[check.name]
                self.setItem(idx, check.col, fn())

    # commands
    def createOneLine(self, filename: str, check: bool = False) -> bool:
        if check and not os.path.exists(filename):
            return False

        new_one = TableItem(filename)
        if self.config["auto_show_image_file"]:
            new_one.autoDetectImage()
        items = self.getProperty_vbao("item_list")
        items.append(new_one)
        self.onDataChanged()
        self.triggerCommandNotifications("add_new", True)
        return True

    def deleteViewRows(self, view_rows: list[int]) -> bool:
        if not view_rows:
            self.triggerCommandNotifications("delete_rows", False)
            return False

        items = self.getProperty_vbao("item_list") or []
        try:
            source_indices = sorted(
                {self.sourceIndexForViewRow(row) for row in view_rows},
                reverse=True,
            )
        except (IndexError, TypeError):
            self.triggerCommandNotifications("delete_rows", False)
            return False

        for source_index in source_indices:
            del items[source_index]

        self.onDataChanged()
        self.triggerCommandNotifications("delete_rows", True)
        return True

    def updateImage(self, view_row: int, image_path: str):
        try:
            item = self.itemForViewRow(view_row)
        except IndexError:
            self.triggerCommandNotifications("update_image", False)
            return

        success = item.setDisplay(image_path)
        self.triggerPropertyNotifications("items")
        self.triggerCommandNotifications("update_image", success)

    def updateTags(self, view_row: int, tags):
        try:
            item = self.itemForViewRow(view_row)
            normalized = normalize_tags(tags)
            self.tag_model.register_existing_tags(normalized)
            item.setTags(self.tag_model.enforce_file_tags(normalized))
        except (IndexError, TagRuleError, TypeError) as exc:
            self._notifyTagError(str(exc))
            self.triggerCommandNotifications("update_tags", False)
            return

        self.onDataChanged()
        self.triggerPropertyNotifications("tag_schema")
        self.triggerCommandNotifications("update_tags", True)

    def setFileTag(self, view_row: int, tag: str, selected: bool):
        try:
            item = self.itemForViewRow(view_row)
            item.setTags(self.tag_model.apply_tag_selection(item.tags, tag, selected))
        except (IndexError, TagRuleError, TypeError) as exc:
            self._notifyTagError(str(exc))
            self.triggerCommandNotifications("toggle_file_tag", False)
            return

        self.onDataChanged()
        self.triggerCommandNotifications("toggle_file_tag", True)

    def _notifyTagError(self, message: str):
        self.setProperty_vbao("tag_error", message)
        self.triggerPropertyNotifications("tag_error")

    def _selectedFilterTags(self) -> list[str]:
        return normalize_tags(
            list(self.tag_filter.exclusive.values()) + list(self.tag_filter.coexist)
        )

    def _restoreFilterFromTags(self, selected_tags):
        exclusive: dict[str, str] = {}
        coexist: list[str] = []
        for tag in normalize_tags(selected_tags):
            if tag not in self.tag_model.all_tags:
                continue
            group = self.tag_model.group_for_tag(tag)
            if group is None:
                coexist.append(tag)
            else:
                exclusive[group.id] = tag
        self.tag_filter = TagFilter(exclusive, coexist)

    def manageTagDefinition(self, action: str, *args):
        items = self.getProperty_vbao("item_list") or []
        selected_filter_tags = self._selectedFilterTags()
        try:
            if action == "add_group":
                self.tag_model.add_group(args[0])
            elif action == "rename_group":
                self.tag_model.rename_group(args[0], args[1])
            elif action == "delete_group":
                self.tag_model.delete_group(args[0])
            elif action == "add_tag":
                self.tag_model.add_tag(args[0], args[1])
            elif action == "rename_tag":
                old_name = normalize_tag_name(args[0])
                new_name = normalize_tag_name(args[1])
                self.tag_model.rename_tag(old_name, new_name)
                selected_filter_tags = [
                    new_name if tag == old_name else tag
                    for tag in selected_filter_tags
                ]
                for item in items:
                    item.setTags(self.tag_model.rename_in_file_tags(
                        item.tags, old_name, new_name
                    ))
            elif action == "delete_tag":
                tag = args[0]
                self.tag_model.delete_tag(tag)
                selected_filter_tags = [
                    selected for selected in selected_filter_tags
                    if selected != tag
                ]
                for item in items:
                    item.setTags(self.tag_model.remove_from_file_tags(item.tags, tag))
            elif action == "move_tag":
                tag, group_id = args[0], args[1]
                self.tag_model.move_tag(tag, group_id)
                if tag in selected_filter_tags:
                    selected_filter_tags.remove(tag)
                    selected_filter_tags.append(tag)
                if group_id is not None:
                    for item in items:
                        if tag in item.tags:
                            item.setTags(self.tag_model.apply_tag_selection(
                                item.tags, tag, True
                            ))
            else:
                raise TagRuleError(f'unknown tag operation: "{action}"')
        except (IndexError, TagRuleError, TypeError, ValueError) as exc:
            self._notifyTagError(str(exc))
            self.triggerCommandNotifications("manage_tags", False)
            return

        self._restoreFilterFromTags(selected_filter_tags)
        self.onDataChanged()
        self.triggerPropertyNotifications("tag_schema")
        self.triggerCommandNotifications("manage_tags", True)

    def setTagFilter(self, exclusive=None, coexist=None):
        self.tag_filter = TagFilter(exclusive or {}, coexist or [])
        self.onDataChanged()
        self.triggerCommandNotifications("filter_tags", True)

    def filterTag(self, tags):
        """Compatibility entry point for the existing text-based filter dialog."""
        self.setTagFilter(coexist=tags)

    def clearTagFilters(self):
        self.tag_filter.clear()
        self.onDataChanged()
        self.triggerCommandNotifications("clear_filters", True)

    def changeWorkDir(self, new_dir: str):
        assert os.path.exists(new_dir)

        # collect file info before change
        valid_items, invalid_items = [], []
        for item in self.getProperty_vbao("item_list"):
            if os.path.exists(item.abs_path):
                valid_items.append(item)
            else:
                invalid_items.append(item)

        # try to move invalid items
        for item in invalid_items:
            rela = os.path.relpath(item.abs_path, self.work_dir)
            new_path = os.path.abspath(os.path.join(new_dir, rela))
            if os.path.exists(new_path):
                item.setFilename(new_path, force=True)

        # update work_dir
        self.setProperty_vbao("work_dir", new_dir)
        self.onDataChanged()
        self.triggerPropertyNotifications("work_dir")
