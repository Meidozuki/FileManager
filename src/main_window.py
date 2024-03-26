import os
from typing import List, Optional

from PySide6.QtCore import QSize, Qt, Slot, QFileInfo
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QMenuBar, QMenu,
    QWidget, QPushButton, QLabel, QFileIconProvider, QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtGui import (
    QIcon, QPixmap, QImage, QAction,
)

from .menu_bar import MenuBar
from .table_item import TableItem

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hello Qt")
        self.resize(QSize(800, 600))

        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)

        self.table = QTableWidget(2,3)
        self.table_layout = QWidget(self)
        self.table_layout.setLayout(self.createTableLayout())

        self.setCentralWidget(self.table_layout)

        self.table.setIconSize(QSize(40,40))
        view = QHeaderView(Qt.Orientation.Vertical)
        view.setDefaultSectionSize(100)
        self.table.setVerticalHeader(view)

        self.payloads = {}


        t = TableItem('01.png')
        t.setDisplay('01.png')
        row = t.toTableWidgetItems()
        self.table.setColumnCount(len(row))
        self.addTableRow(0, row)

        t2 = TableItem('main.py')
        icon = QFileIconProvider().icon(QFileInfo('main.py'))

        row = t2.toTableWidgetItems()
        row[1].setIcon(icon)
        self.addTableRow(1, row)

        # m = model.Model()
        # print(m.save([t,t2,t],'temp'))

    def createTableLayout(self):
        """need setLayout() to reparent"""
        outer = QVBoxLayout()

        buttons = QHBoxLayout()
        test_button = QPushButton("test button")
        @Slot()
        def log():
            print("clicked")
        test_button.clicked.connect(log)

        button = QPushButton("add")
        button.clicked.connect(self.commandAddNewFiles)

        buttons.addWidget(test_button)
        buttons.addWidget(button)

        outer.addLayout(buttons)
        outer.addWidget(self.table)
        return outer

    @Slot()
    def commandAddNewFiles(self):
        if (self.getSelectedFileFromUser()):
            names = self.payloads["file_select"]
            for name in names:
                item = TableItem(name)
                idx = self.table.rowCount()
                self.table.insertRow(idx)
                self.addTableRow(idx, item.toTableWidgetItems())

    def getSelectedFileFromUser(self) -> bool:
        # [from doc] If parent is not None, the dialog will be shown centered over the parent widget.
        names, category = QFileDialog.getOpenFileNames(None, "Select files to add")
        if names:
            self.payloads["file_select"] = names
            return True
        else:
            return False

    def prepareMenuBar(self):
        menu1 = QMenu(self.menu_bar)
        menu1.setTitle("menu1")
        self.menu_bar.addMenu(menu1)

        menu1.addAction(QAction("sub1", menu1))

    def addTableRow(self, row, ls: List[QTableWidgetItem | QWidget]):
        for i,ctx in enumerate(ls):
            if isinstance(ctx, QTableWidgetItem):
                self.table.setItem(row, i, ctx)
            elif isinstance(ctx, QPushButton):
                self.table.setCellWidget(row, i, ctx)
            else:
                raise TypeError