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

        self.setWindowTitle("Hello Qt")
        self.resize(QSize(800, 600))

        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)

        self.viewmodel = ViewModel()
        self.view = QTableView()
        self.setupTableView()
        i = self.viewmodel.index(0,2)
        b = QPushButton("abc")
        self.view.setIndexWidget(i, b)

        self.table_layout = QWidget(self)
        self.table_layout.setLayout(self.createTableLayout())

        self.setCentralWidget(self.table_layout)

        vbao.App.bind(self.viewmodel.model, self.viewmodel, self, True)
        self.viewmodel.init('temp/temp')


        # self.payloads = {}


        # t = TableItem('01.png')
        # t.setDisplay('01.png')
        # row = t.toTableWidgetItems()
        # self.table.setColumnCount(len(row))
        # self.addTableRow(0, row)
        #
        # t2 = TableItem('main.py')
        # icon = QFileIconProvider().icon(QFileInfo('main.py'))

    def getIndex(self, i, j):
        return self.view.model().index(i, j)

    def setupTableView(self):
        self.view.setModel(self.viewmodel)

        self.view.setIconSize(QSize(40,40))

        header_view = QHeaderView(Qt.Orientation.Vertical, None)
        header_view.setDefaultSectionSize(100)
        self.view.setVerticalHeader(header_view)

        # self.view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

    def updateDataFrame(self):
        for i, row_data in enumerate(self.getProperty('item_list')):
            for j, ctx in enumerate(row_data.toTableWidgetItems()):
                if isinstance(ctx, QStandardItem):
                    pass
                elif isinstance(ctx, QPushButton):
                    self.view.setIndexWidget(self.getIndex(i,j), ctx)
                else:
                    raise TypeError


    def createTableLayout(self):
        """need setLayout() to reparent"""
        outer_v = QVBoxLayout()

        inner_h = QHBoxLayout()
        test_button = QPushButton("test button")
        test_button.clicked.connect(self.testFn)

        button = QPushButton("add")
        button.clicked.connect(self.commandAddNewFiles)

        inner_h.addWidget(test_button)
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
        # QFileDialog.getSaveFileName()

        if names:
            for name in names:
                self.commands["add_file"].setParameter(name)
                self.runCommand("add_file")

    @Slot()
    def commandOpenFile(self):
        selected_file = ''


class ViewPropListener(vbao.PropertyListenerBase):
    def onPropertyChanged(self, prop_name: str):
        match prop_name:
            case 'current_df':
                self.master.updateDataFrame()
            case _:
                print('uncaught prop '+prop_name)