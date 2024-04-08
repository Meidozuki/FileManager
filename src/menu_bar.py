from functools import wraps
from typing import *

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

    def createSubmenu(self, parent: QMenu, strings: List[str], slots: List[Optional[Any]]):
        for string, slot in zip(strings, slots):
            action = QAction(string, parent)
            if slot:
                action.triggered.connect(slot)
            parent.addAction(action)

    def constructTableOpMenu(self):
        file_menu = QMenu(u"File", self)
        self.addMenu(file_menu)

        names = [u"Save to...", u"Load from...", u"Clear"]
        actions = [self.trySaveCommand, self.tryLoadCommand, self.clearCommand]
        self.createSubmenu(file_menu, names, actions)

    @Slot()
    def trySaveCommand(self):
        path, category = QFileDialog.getSaveFileName(self, "Save file")
        if path:
            self.parent().getCommand("save").directCall(path)

    @Slot()
    def tryLoadCommand(self):
        path, category = QFileDialog.getOpenFileName(self, "Load file")
        if path:
            self.parent().getCommand("load").directCall(path)

    @Slot()
    def clearCommand(self):
        self.parent().runCommand("clear")
