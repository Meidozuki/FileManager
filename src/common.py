import os
from typing import Optional

from PySide6.QtCore import QSize, QFileInfo
from PySide6.QtWidgets import (
    QFileIconProvider,
    QTableWidget, QTableWidgetItem)
from PySide6.QtGui import QIcon, QPixmap, QAbstractFileIconProvider


def getFileIcon(filename: str) -> Optional[QIcon]:
    if os.path.exists(filename):
        provider = QFileIconProvider()
        return provider.icon(QFileInfo(filename))
    else:
        return None