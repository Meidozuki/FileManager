import logging
from easydict import EasyDict
from functools import wraps
from typing import *

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QMenuBar, QMenu, QFileDialog, QInputDialog, QPushButton
)
from PySide6.QtGui import QAction

from i18n import LOCTEXT

def createQuickButtons(window):
    def button_with_text(text:str):
        button = QPushButton()
        button.setText(text)
        return button
    layout_h = QHBoxLayout()

    button = button_with_text(LOCTEXT(u'添加文件'))
    button.clicked.connect(window.commandAddNewFiles)
    layout_h.addWidget(button)

    button = button_with_text(LOCTEXT(u'设置预览图'))
    button.clicked.connect(window.commandUpdateImage)
    layout_h.addWidget(button)

    button = button_with_text(LOCTEXT(u'设置标签'))
    button.clicked.connect(window.commandSetTags)
    layout_h.addWidget(button)

    test_button = QPushButton("test button")
    test_button.clicked.connect(window.testFn)
    layout_h.addWidget(test_button)

    button = button_with_text(LOCTEXT(u'打开所在文件夹'))
    button.clicked.connect(window.commandOpenFolder)
    layout_h.addWidget(button)

    button = button_with_text(LOCTEXT(u'打开文件'))
    layout_h.addWidget(button)
    button.clicked.connect(window.commandOpenFile)
    return layout_h


class MenuBar(QMenuBar):
    @wraps(QMenuBar.__init__)
    def __init__(self, parent):
        super().__init__(parent)

        self.menu_table = {
            0: EasyDict({
                "menu_name": LOCTEXT(u'表格操作'),
                "sub_actions": [
                    u"Change work dir", u"------",u"Save to...", u"Load from...", u"Clear",
                ],
                "callbacks": [
                    self.cdCommand, self.emptyCallback, self.trySaveCommand, self.tryLoadCommand, self.clearCommand
                ]
            }),
            1: EasyDict({
                "menu_name": u"Filter",
                "sub_actions": [
                    u"Filter tags", u"Clear filters"
                ],
                "callbacks": [
                    self.filterTagCommand, self.clearFilterCommand
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

            act, cb = menu_item.sub_actions, menu_item.callbacks
            if len(act) != len(cb):
                logging.warning(f"menu {menu.title()}'s actions and callbacks do not match, are\n"
                                f"{act}\nand {cb}")
            createSubmenu(menu, act, cb)

    @Slot()
    def trySaveCommand(self):
        path, category = QFileDialog.getSaveFileName(self, "Save file", self.parent().temp_dir,
                                                     filter=self.parent().save_format)
        if path:
            self.parent().getCommand("save").directCall(path)

    @Slot()
    def tryLoadCommand(self):
        path, category = QFileDialog.getOpenFileName(self, "Load file", self.parent().temp_dir,
                                                     filter=self.parent().save_format)
        if path:
            self.parent().getCommand("load").directCall(path)

    @Slot()
    def clearCommand(self):
        self.parent().runCommand("clear")

    @Slot()
    def cdCommand(self):
        path: str = QFileDialog.getExistingDirectory(None)
        self.parent().getCommand("change_dir").directCall(path)

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
