import os
from typing import List, Optional, Union, Tuple

from PySide6.QtCore import QSize, Qt, Slot, QFileInfo, QModelIndex
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QMenuBar, QMenu,
    QWidget, QPushButton, QLabel, QFileIconProvider, QFileDialog, QInputDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QTableView, QAbstractItemView)
from PySide6.QtGui import (
    QIcon, QPixmap, QImage, QAction, QStandardItemModel, QStandardItem,
)

from .vbao_wrapper import vbao
from .viewmodel import ViewModel
from .ui import MenuBar, createQuickButtons
from .table_item import TableItem


class MainWindow(QMainWindow, vbao.View):
    def __init__(self):
        super().__init__()

        self.prop_listener = ViewPropListener(self)
        self.cmd_listener = ViewCmdListener(self)

        self.setWindowTitle("Hello Qt")
        self.resize(QSize(800, 600))

        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)

        self.viewmodel = ViewModel()
        self.view = QTableView()
        self.setupTableView()

        self.layout_widget = self.createTableLayout()
        self.setCentralWidget(self.layout_widget)

        vbao.App.bind(self.viewmodel.model, self.viewmodel, self, True)
        self.viewmodel.init()

    @property
    def selectedIndexes(self) -> set:
        return set([i.row() for i in self.view.selectedIndexes()])

    @property
    def selectedOneRow(self) -> Union[bool, Tuple[bool, int]]:
        """
        return only False when invalid, to simplify if statement
        """
        if len(self.selectedIndexes) != 1:
            return False
        else:
            return True, list(self.selectedIndexes)[0]

    @property
    def save_format(self):
        return self.getProperty('save_format')

    @property
    def temp_dir(self):
        return self.getProperty("temp_dir")

    def getIndex(self, i, j):
        return self.view.model().index(i, j)

    def setIndexWidget(self, i, j, widget: QWidget):
        self.view.setIndexWidget(self.getIndex(i, j), widget)

    def setupTableView(self):
        self.view.setModel(self.viewmodel)

        self.view.setIconSize(QSize(30, 30))

        header_view = QHeaderView(Qt.Orientation.Vertical, None)
        header_view.setDefaultSectionSize(100)
        self.view.setVerticalHeader(header_view)

        self.view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    def updateData(self):
        ls = self.getProperty("item_list")
        index = self.getProperty_vbao("filter_index")
        if index is None:
            index = range(len(ls))
        for row, idx in enumerate(index):
            row_data = ls[idx]
            pixmap = row_data.getPreviewImage()
            if pixmap is not None:
                preview_image = QLabel()
                preview_image.setPixmap(pixmap)
                self.setIndexWidget(row, 1, preview_image)
            else:
                self.viewmodel.setItem(row, 1, QStandardItem("None"))

    def createTableLayout(self):
        """setLayout() will auto parent"""
        parent = QWidget(self)

        outer_v = QVBoxLayout()

        inner_h = createQuickButtons(self)
        label = QLabel("Current directory: ")
        label.setObjectName("work dir display")

        outer_v.addLayout(inner_h)
        outer_v.addWidget(self.view)
        outer_v.addWidget(label)

        parent.setLayout(outer_v)
        return parent

    # button slots
    @Slot()
    def testFn(self):
        print(self.selectedOneRow)

    @Slot()
    def commandOpenFolder(self):
        if self.selectedOneRow:
            row = self.selectedOneRow[1]
            item = self.view.model().item(row, 2)
            path = os.path.abspath(item.text() + '/..')
            # TODO:为什么这里用explorer就会跳到我的文档？？？ （替换为用start）
            self.getCommand("open").directCall('powershell', 'start ' + path)

    @Slot()
    def commandOpenFile(self):
        if self.selectedOneRow:
            row = self.selectedOneRow[1]
            item = self.view.model().item(row, 2)
            path = item.text()
            self.getCommand("open").directCall('powershell', 'start ' + path)

    @Slot()
    def commandAddNewFiles(self):
        # [from doc] If parent is not None, the dialog will be shown centered over the parent widget.
        names, category = QFileDialog.getOpenFileNames(None, "Select files to add")

        if names:
            for name in names:
                self.getCommand("add_file").directCall(name)

    @Slot()
    def commandUpdateImage(self):
        rows = self.selectedOneRow
        if rows:
            name, category = QFileDialog.getOpenFileName(None, "Select preview image")
            if name:
                self.getCommand("update_image").directCall(rows[1], name)

    @Slot()
    def commandSetTags(self):
        rows = self.selectedOneRow
        if rows:
            tags, ok = QInputDialog.getText(self, "title", "Please input tags")
            if ok:
                self.getCommand("update_tags").directCall(rows[1], tags)


class ViewPropListener(vbao.PropertyListenerBase):
    def onPropertyChanged(self, prop_name: str):
        match prop_name:
            case 'items':
                self.master.updateData()
            case 'work_dir':
                label = self.master.layout_widget.findChild(QLabel, "work dir display")
                label.setText("Current directory: " + self.master.getProperty("work_dir"))
            case _:
                print('uncaught prop ' + prop_name)


class ViewCmdListener(vbao.CommandListenerBase):
    def onCommandComplete(self, cmd_name: str, success: bool):
        print(f"Command {cmd_name} success:{success}")
        match cmd_name:
            case 'clear':
                self.master.view.reset()
