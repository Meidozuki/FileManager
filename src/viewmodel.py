import os.path

from .vbao_wrapper import vbao
# import vbao
import pandas as pd
import logging
from typing import List


from PySide6.QtCore import QSize, Qt, Slot, QFileInfo, QAbstractTableModel
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QMenuBar, QMenu,
    QWidget, QPushButton, QLabel, QFileIconProvider, QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QTableView, QListView, QTreeView)
from PySide6.QtGui import (
    QIcon, QPixmap, QImage, QAction, QStandardItemModel, QStandardItem
)

from .model import Model, TableItem
from .vm_commands import *


class ViewModel(QStandardItemModel,vbao.ViewModel):
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
            col_count = len(mediate[0].toTableWidgetItems())
            if self.columnCount() < col_count:
                self.setColumnCount(col_count)

        for i, data in enumerate(mediate):
            self.addTableRow(i, data.toTableWidgetItems())

        self.triggerPropertyNotifications("current_df")


    def addTableRow(self, row, ls: List[QTableWidgetItem | QWidget]):
        for i, ctx in enumerate(ls):
            if isinstance(ctx, QStandardItem):
                self.setItem(row, i, ctx)
            elif isinstance(ctx, QPushButton):
                pass
                # self.setCellWidget(row, i, ctx)
            else:
                raise TypeError

    # commands
    def createOneLine(self, filename: str, check: bool = False) -> bool:
        if check and not os.path.exists(filename):
            return False

        new_one = TableItem(filename)
        self.addTableRow(self.rowCount(), new_one.toTableWidgetItems())


class VMListener(vbao.PropertyListenerBase):
    def onPropertyChanged(self, prop_name: str):
        pass