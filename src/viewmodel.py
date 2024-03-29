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


class ViewModel(vbao.ViewModel, QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.model = Model()

        self.view = None  # share from TableView
        df = self.loadData('temp/temp')
        print(df)
        self.reformTableModel(df)

        self.commands["add_file"] = CommandTryAddClass(self)


    def loadData(self, filename):
        """load data from disk"""
        df = self.model.load(filename)
        df = df.where(pd.notnull, None)
        self.properties["df"] = df
        return df

    def reformTableModel(self, df: pd.DataFrame):
        """from df to Qt TableModel"""
        shape = df.shape
        self.setRowCount(shape[0])
        self.setColumnCount(shape[1])

        mediate = TableItem.fromRecords(df)
        self.properties["current_items"] = mediate
        for i, data in enumerate(mediate):
            self.addTableRow(i, data.toTableWidgetItems())

    def propagateToView(self, view: QTableView, data: List[TableItem]):
        for idx, item in enumerate(data):
            pass
        self.setItem()


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
