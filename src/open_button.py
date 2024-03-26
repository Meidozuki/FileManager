import shlex, subprocess
from functools import wraps

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QPushButton
)


class FileOpenButton(QPushButton):
    @wraps(QPushButton.__init__)
    def __init__(self, text="open", *args, **kwargs):
        super().__init__(text, *args, **kwargs)
        # explorer会调用默认程序，对于目录会打开文件管理器
        self.open_program = 'explorer'
        self.overload = None
        self.clicked.connect(self.onClicked)

    def setOverload(self, overload: str):
        self.overload = overload

    @Slot()
    def onClicked(self):
        args = [self.open_program] + shlex.split(self.overload)
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.stderr:
            print(result.args)
            print(result.stderr)