from functools import wraps

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QMenuBar, QMenu, QFileDialog,
    QWidget, QPushButton, QLabel)
from PySide6.QtGui import QIcon, QPixmap, QImage, QAction


class MenuBar(QMenuBar):
    @wraps(QMenuBar.__init__)
    def __init__(self, parent):
        super().__init__(parent)
        self.constructTableOpMenu()


    def constructTableOpMenu(self):
        file_menu = QMenu(u"File", self)
        self.addMenu(file_menu)

        sub1 = QAction(u"save", file_menu)
        sub1.triggered.connect(self.trySaveCommand)
        file_menu.addAction(sub1)

        sub2 = QAction(u"clear", file_menu)
        sub2.triggered.connect(self.clearCommand)
        file_menu.addAction(sub2)

    @Slot()
    def trySaveCommand(self):
        path, category = QFileDialog.getSaveFileName(None, "Save file")
        if path:
            self.parent().getCommand("save").setParameter(path)
            self.parent().runCommand("save")

    @Slot()
    def clearCommand(self):
        self.parent().runCommand("clear")