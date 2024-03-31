import os
import logging
import pandas as pd

from PySide6.QtCore import QSize, Qt, Slot, QFileInfo
from PySide6.QtWidgets import (
    QWidget, QPushButton, QLabel, QFileIconProvider, QFileDialog,
    )
from PySide6.QtGui import (
    QIcon, QPixmap, QImage, QStandardItemModel, QStandardItem
)

from .vbao_wrapper import vbao
# import vbao
from .table_item import TableItem, TableItemChecklist
from .model import Model
from .vm_commands import *
from .common import getFileIcon


class ViewModel(QStandardItemModel, vbao.ViewModel):
    """
    viewmodel存储从dataframe转化而来的信息
    """

    def __init__(self, parent=None, ):
        super().__init__(parent)

        self.model = Model()

        self.setCommand("add_file", CommandTryAddClass(self))

    def init(self, start_load_path: str = ''):
        self._df = self.loadData(start_load_path)
        print(self._df)
        self.setProperty_vbao("current_df", self._df)
        self.onDataFrameChanged()

    def loadData(self, filename):
        """load data from disk"""
        df = self.model.load(filename)
        df = df.where(pd.notnull, None)
        # self.properties["df"] = df
        return df

    def onDataFrameChanged(self):
        df = self.getProperty("current_df")
        shape = df.shape
        self.setRowCount(shape[0])

        mediate = TableItem.fromRecords(df)
        self.setProperty_vbao("item_list", mediate)
        if mediate:
            col_count = mediate[0].expected_cols
            if self.columnCount() < col_count:
                self.setColumnCount(col_count)

            for i, data in enumerate(mediate):
                self.addTableRow(i, data)

    def addTableRow(self, idx, item: TableItem):
        viewer = {'short_name': lambda: QStandardItem(item.short_name),
                  'full_name': lambda: QStandardItem(item.full_name),
                  'short_name_icon': lambda: QStandardItem(item.icon, item.short_name),
                  'icon': lambda: QStandardItem(item.icon, ''),
                  'empty': lambda: QStandardItem()
                  }

        for check in item.checklist:
            if check.role == TableItemChecklist.ModelRole:
                # immediately throw KeyError if not match
                fn = viewer[check.name]
                self.setItem(idx, check.col, fn())

        self.triggerPropertyNotifications("current_df")

    # commands
    def createOneLine(self, filename: str, check: bool = False) -> bool:
        if check and not os.path.exists(filename):
            return False

        new_one = TableItem(filename)
        self.addTableRow(self.rowCount(), new_one)


class VMListener(vbao.PropertyListenerBase):
    def onPropertyChanged(self, prop_name: str):
        pass
