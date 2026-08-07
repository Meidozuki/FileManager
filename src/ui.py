from functools import wraps

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QHBoxLayout, QMenuBar, QMenu, QFileDialog, QPushButton
from PySide6.QtGui import QAction

from src.i18n import LOCTEXT

def createQuickButtons(window):
    def button_with_text(text: str, object_name: str, tooltip: str):
        button = QPushButton(text)
        button.setObjectName(object_name)
        button.setToolTip(tooltip)
        return button

    layout_h = QHBoxLayout()
    layout_h.setContentsMargins(12, 10, 12, 10)
    layout_h.setSpacing(8)

    button = button_with_text(
        LOCTEXT(u'添加文件'), "primaryButton", "将一个或多个文件添加到列表",
    )
    button.clicked.connect(window.commandAddNewFiles)
    layout_h.addWidget(button)

    button = button_with_text(
        LOCTEXT(u'设置预览图'), "secondaryButton", "为选中的文件设置预览图",
    )
    button.clicked.connect(window.commandUpdateImage)
    layout_h.addWidget(button)

    button = button_with_text(
        LOCTEXT(u'设置标签'), "secondaryButton", "编辑选中文件的 Tag",
    )
    button.clicked.connect(window.commandSetTags)
    layout_h.addWidget(button)

    layout_h.addStretch()

    button = button_with_text(
        LOCTEXT(u'打开所在文件夹'), "quietButton", "在资源管理器中打开文件所在目录",
    )
    button.clicked.connect(window.commandOpenFolder)
    layout_h.addWidget(button)

    button = button_with_text(
        LOCTEXT(u'打开文件'), "secondaryButton", "使用系统默认程序打开选中文件",
    )
    button.clicked.connect(window.commandOpenFile)
    layout_h.addWidget(button)
    return layout_h


class MenuBar(QMenuBar):
    @wraps(QMenuBar.__init__)
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("mainMenuBar")
        self.constructTableOpMenu()

    @staticmethod
    def _add_action(menu: QMenu, text: str, slot, shortcut: str | None = None):
        action = QAction(text, menu)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(slot)
        menu.addAction(action)
        return action

    def constructTableOpMenu(self):
        self.file_menu = QMenu(LOCTEXT(u"文件"), self)
        self.addMenu(self.file_menu)
        self._add_action(self.file_menu, LOCTEXT(u"添加文件"), self.parent().commandAddNewFiles)
        self._add_action(self.file_menu, LOCTEXT(u"更改工作目录"), self.cdCommand)
        self.file_menu.addSeparator()
        self._add_action(self.file_menu, LOCTEXT(u"加载列表…"), self.tryLoadCommand, "Ctrl+O")
        self._add_action(self.file_menu, LOCTEXT(u"保存列表…"), self.trySaveCommand, "Ctrl+S")
        self.file_menu.addSeparator()
        self._add_action(self.file_menu, LOCTEXT(u"清空列表"), self.clearCommand)

        self.tag_menu = QMenu("Tag", self)
        self.addMenu(self.tag_menu)
        self._add_action(self.tag_menu, LOCTEXT(u"管理 Tag…"), self.parent().commandOpenTagManager)
        self._add_action(self.tag_menu, LOCTEXT(u"清除 Tag 筛选"), self.clearFilterCommand)

    @Slot()
    def trySaveCommand(self):
        path, category = QFileDialog.getSaveFileName(
            self, "保存文件列表", self.parent().temp_dir,
            filter=self.parent().save_format,
        )
        if path:
            self.parent().getCommand("save").directCall(path)

    @Slot()
    def tryLoadCommand(self):
        path, category = QFileDialog.getOpenFileName(
            self, "加载文件列表", self.parent().temp_dir,
            filter=self.parent().save_format,
        )
        if path:
            self.parent().getCommand("load").directCall(path)

    @Slot()
    def clearCommand(self):
        self.parent().runCommand("clear")

    @Slot()
    def cdCommand(self):
        path: str = QFileDialog.getExistingDirectory(self, "选择工作目录")
        if path:
            self.parent().getCommand("change_dir").directCall(path)

    @Slot()
    def clearFilterCommand(self):
        self.parent().runCommand("clear_filters")
