from easydict import EasyDict
from functools import wraps
from typing import *

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QMenuBar, QMenu, QFileDialog, QInputDialog
)
from PySide6.QtGui import QAction


class MenuBar(QMenuBar):
    @wraps(QMenuBar.__init__)
    def __init__(self, parent):
        super().__init__(parent)

        self.menu_table = {
            0: EasyDict({
                "menu_name": u"Table",
                "sub_actions": [
                    u"Save to...", u"Load from...", u"Clear",
                ],
                "callbacks": [
                    self.trySaveCommand, self.tryLoadCommand, self.clearCommand
                ]
            }),
            1: EasyDict({
                "menu_name": u"Filter",
                "sub_actions": [
                    u"Filter tags", u"Clear filters", "test"
                ],
                "callbacks": [
                    self.filterTagCommand, self.clearFilterCommand, None
                ]
            }),
        }

        self.constructTableOpMenu()

    def constructTableOpMenu(self):
        def createSubmenu(parent: QMenu, strings: List[str], slots: List[Optional[Any]]):
            for string, slot in zip(strings, slots):
                action = QAction(string, parent)
                if slot:
                    action.triggered.connect(slot)
                else:
                    action.setText(action.text() + "_no-bind")
                parent.addAction(action)

        for menu_item in self.menu_table.values():
            menu = QMenu(menu_item.menu_name, self)
            self.addMenu(menu)

            createSubmenu(menu, menu_item.sub_actions, menu_item.callbacks)

    @Slot()
    def trySaveCommand(self):
        path, category = QFileDialog.getSaveFileName(self, "Save file", filter=self.parent().save_format)
        if path:
            self.parent().getCommand("save").directCall(path)

    @Slot()
    def tryLoadCommand(self):
        path, category = QFileDialog.getOpenFileName(self, "Load file", filter=self.parent().save_format)
        if path:
            self.parent().getCommand("load").directCall(path)

    @Slot()
    def clearCommand(self):
        self.parent().runCommand("clear")

    @Slot()
    def filterTagCommand(self):
        tags, ok = QInputDialog.getText(self, "title", "Please input tags")
        if ok:
            self.parent().getCommand("filter_tags").directCall(tags)

    @Slot()
    def clearFilterCommand(self):
        self.parent().runCommand("clear_filters")

    @Slot()
    def emptyCallback(self):
        pass
