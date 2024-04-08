import os
from typing import List, Optional

from PySide6.QtCore import QSize, Qt, Slot, QFileInfo, QModelIndex
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QMenuBar, QMenu,
    QWidget, QPushButton, QLabel, QFileIconProvider, QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QTableView, QAbstractItemView)
from PySide6.QtGui import (
    QIcon, QPixmap, QImage, QAction, QStandardItemModel, QStandardItem,
)

from .vbao_wrapper import vbao
from .viewmodel import ViewModel
from .menu_bar import MenuBar
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

        self.table_layout = QWidget(self)
        self.table_layout.setLayout(self.createTableLayout())

        self.setCentralWidget(self.table_layout)

        vbao.App.bind(self.viewmodel.model, self.viewmodel, self, True)
        self.viewmodel.init()

    @property
    def selectedIndexes(self) -> set:
        return set([i.row() for i in self.view.selectedIndexes()])

    @property
    def save_format(self):
        return self.getProperty('save_format')

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

    def updateDataFrame(self):
        for i, row_data in enumerate(self.getProperty('item_list')):
            pixmap = row_data.getPreviewImage()
            if pixmap is not None:
                preview_image = QLabel()
                preview_image.setPixmap(pixmap)
                self.setIndexWidget(i, 1, preview_image)
            else:
                self.viewmodel.setItem(i, 1, QStandardItem("None"))

    def createTableLayout(self):
        """need setLayout() to reparent"""
        outer_v = QVBoxLayout()

        inner_h = QHBoxLayout()
        test_button = QPushButton("test button")
        test_button.clicked.connect(self.testFn)
        inner_h.addWidget(test_button)

        button = QPushButton("add")
        button.clicked.connect(self.commandAddNewFiles)
        inner_h.addWidget(button)

        button = QPushButton("set image")
        button.clicked.connect(self.commandUpdateImage)
        inner_h.addWidget(button)

        outer_v.addLayout(inner_h)
        outer_v.addWidget(self.view)
        return outer_v

    def prepareMenuBar(self):
        menu1 = QMenu(self.menu_bar)
        menu1.setTitle("menu1")
        self.menu_bar.addMenu(menu1)

        menu1.addAction(QAction("sub1", menu1))

    @Slot()
    def testFn(self):
        print(self.view.selectedIndexes())

    @Slot()
    def commandAddNewFiles(self):
        # [from doc] If parent is not None, the dialog will be shown centered over the parent widget.
        names, category = QFileDialog.getOpenFileNames(None, "Select files to add")

        if names:
            for name in names:
                self.getCommand("add_file").directCall(name)

    @Slot()
    def commandUpdateImage(self):
        name, category = QFileDialog.getOpenFileName(None, "Select preview image")
        if name:
            selected = self.selectedIndexes
            if len(selected) != 1:
                print("please select a row to update")
                return
            self.getCommand("update_image").directCall(*selected, name)

    @Slot()
    def commandOpenFile(self):
        selected_file = ''


class ViewPropListener(vbao.PropertyListenerBase):
    def onPropertyChanged(self, prop_name: str):
        match prop_name:
            case 'current_df':
                self.master.updateDataFrame()
            case _:
                print('uncaught prop ' + prop_name)


class ViewCmdListener(vbao.CommandListenerBase):
    def onCommandComplete(self, cmd_name: str, success: bool):
        print(f"Command {cmd_name} success:{success}")
        match cmd_name:
            case 'clear':
                self.master.view.reset()
