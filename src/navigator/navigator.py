
import numpy as np
from dataclasses import dataclass
from typing import Optional, TypeAlias

from PySide6.QtCore import QSize, Slot, QCoreApplication
from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QPushButton, QSizePolicy)

from src.main_window import MainWindow
from src.submodules import WindowRenameSuffix


@dataclass(frozen=True)
class NavigatorTableItem:
    key: str
    text: str
    window_cls: type[object]

    def __post_init__(self):
        assert isinstance(self.key, str)
        assert isinstance(self.text, str)
        assert issubclass(self.window_cls, object)


_navigator_table = [
    NavigatorTableItem("default", "MainWindow", MainWindow),
    NavigatorTableItem("rename", "重命名文件后缀", WindowRenameSuffix),
    NavigatorTableItem("1", "Placeholder", object),
]

_navigator_settings = {
    'size': QSize(400, 300),
    'lr_margin': 0.1,
    'tb_margin': 0
}

_SimpleNumber: TypeAlias = int | float


class NavigatorTableHelper:
    @classmethod
    def get(cls) -> list[NavigatorTableItem]:
        return _navigator_table


class NavigatorWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(QCoreApplication.translate(
            "Hello", "Hello"
        ))

        self.central_widget = QWidget(self)
        self.vertical_layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        self.settings = _navigator_settings
        self.resize(self.settings['size'])
        self.set_margin(self.vertical_layout, self.settings['lr_margin'])

        for item in NavigatorTableHelper.get():
            button = QPushButton(self)
            button.setText(item.text)
            button.clicked.connect(self.create_subwindow_callback(item.window_cls))

            self.vertical_layout.addWidget(button)
            self.set_button_height(button, 30)

    def set_margin(self, widget: QWidget,
                   lr_ratio: _SimpleNumber = 0,
                   tb_ratio: _SimpleNumber = 0):
        lr_ratio = np.clip(lr_ratio, 0.0, 1.0)
        tb_ratio = np.clip(tb_ratio, 0.0, 1.0)
        size = self.size()
        w, h = size.width(), size.height()
        left = w * lr_ratio
        top = h * tb_ratio
        widget.setContentsMargins(left, top, left, top)

    def set_button_height(self, button: QPushButton,
                          height: Optional[_SimpleNumber] = None):
        # See https://doc.qt.io/qt-6/qsizepolicy.html
        # TODO: modify button style here
        if height is None: return
        if height <= 0: return

        w = button.size().width()
        if height <= 1:
            h = self.size().height() * height
        else:
            h = height
        h = max(h, button.sizeHint().height())

        button.setMinimumHeight(h)
        policy = button.sizePolicy()
        policy.setVerticalPolicy(QSizePolicy.Policy.Minimum)
        button.setSizePolicy(policy)

    def create_subwindow_callback(self, cls):
        def inner():
            msg = f"navigator clicked, trying create sub-window class: {cls}"
            print(msg)
            if issubclass(cls, QMainWindow):
                window = cls()
                window.show()
                self.link = window  # 保持引用计数，否则会在离开函数时被gc
                self.close()

        return Slot()(inner)
