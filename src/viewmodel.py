import json
import os
import logging

import numpy as np
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
from .common import changeFileExt
from .model import Model
from .vm_commands import *


class ViewModel(QStandardItemModel, vbao.ViewModel):
    """
    viewmodel存储从dataframe转化而来的信息
    item_list 存储总共的、用于保存的信息
    """

    # initialize
    def __init__(self, parent=None, ):
        super().__init__(parent)

        self.model = Model()
        self.setListener(vbao.DummyPropListener())

        self.registerCommands({
            "clear": CommandClear(self),
            "save": CommandSave(self),
            "load": CommandLoad(self),
            "add_file": CommandAddTableRow,
            "update_image": CommandUpdatePreviewImage,
            "update_tags": CommandUpdateTags,
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
        if os.path.exists(start_load_path):
            df = self.loadData(start_load_path)
            df = self.model.prune(df)
            self.setProperty_vbao("item_list", TableItem.fromRecords(df))

        self.setProperty_vbao("work_dir", os.getcwd())
        self.triggerPropertyNotifications("work_dir")

    def clear(self):
        self.setProperty_vbao("filter_index", None)
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

    # save/load
    def loadData(self, filename):
        """load data from disk"""
        # process data
        df = self.model.load(filename)
        print(df)

        shape = df.shape
        self.setRowCount(shape[0])
        if shape[0] > 0:
            df["tags"] = df["tags"].apply(lambda s: s.split(", ") if s else [])

        self.setProperty_vbao('item_list', TableItem.fromRecords(df))

        # process env
        json_name = changeFileExt(filename, 'json')
        if os.path.exists(json_name):
            with open(json_name, 'r') as f:
                d = json.load(f)

            work_dir = d["work_dir"]
            if os.path.exists(work_dir):
                self.setProperty_vbao("work_dir", work_dir)
                self.triggerPropertyNotifications("work_dir")

        self.onDataChanged()
        return df

    def _getWorkEnv(self):
        return {
            "work_dir": self.work_dir
        }

    def saveData(self, filename):
        if self.model.save(self.getProperty("item_list"), filename) is not None:
            with open(changeFileExt(filename, 'json'), 'w') as f:
                json.dump(self._getWorkEnv(), f)
            self.triggerCommandNotifications("save", True)
        else:
            self.triggerCommandNotifications("save", False)

    def onDataChanged(self):
        ls = self.getProperty("item_list")
        index = self.getProperty_vbao("filter_index")
        if index is None:
            index = range(len(ls))

        self.setRowCount(len(index))
        if ls:
            col_count = ls[0].expected_cols
            if self.columnCount() < col_count:
                self.setColumnCount(col_count)

            for row, idx in enumerate(index):
                item: TableItem = ls[idx]
                if self.config["auto_show_image_file"]:
                    item.autoDetectImage()
                self.addTableRow(row, item)

            self.triggerPropertyNotifications("items")

    def addTableRow(self, idx, item: TableItem):
        viewer = {'short_name': lambda: QStandardItem(item.short_name),
                  'short_name_icon': lambda: QStandardItem(item.icon, item.short_name),
                  'rela_path': lambda: QStandardItem(os.path.relpath(item.abs_path, self.work_dir)),
                  'abs_path': lambda: QStandardItem(item.abs_path),
                  'icon': lambda: QStandardItem(item.icon, ''),
                  'tags': lambda: QStandardItem(str(item.tags)),
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
        ls = self.getProperty_vbao("item_list")
        ls.append(new_one)
        self.addTableRow(self.rowCount(), new_one)
        self.triggerPropertyNotifications("items")
        self.triggerCommandNotifications("add_new", True)

    def updateImage(self, row, image_path):
        ls = self.getProperty_vbao("item_list")
        if row < len(ls):
            item: TableItem = ls[row]
            success = item.setDisplay(image_path)
            self.triggerPropertyNotifications('items')
            self.triggerCommandNotifications("update_image", success)
        else:
            self.triggerCommandNotifications("update_image", False)

    def updateTags(self, row, tags):
        tags = tags.replace(', ', ',').split(',')
        self.getProperty_vbao("item_list")[row].tags = tags
        self.onDataChanged()

    def filterTag(self, tag):
        df = self.model.changeItemToDf(self.getProperty_vbao("item_list"))
        print(f"before filter tag {tag}, length is {df.shape[0]}")
        df = df[df["tags"].apply(lambda ls: tag in ls)]
        print(f"after filter tag {tag}, length is {df.shape[0]}")
        self.setProperty_vbao("filter_index", df.index)
        self.onDataChanged()

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
