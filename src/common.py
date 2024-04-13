import os
import re
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


def setupOneFileCategory(name: str, suffix: list):
    """
    convert to QFileDialog format
    example: setupOneFileCategory('image', ['jpg','png'])
    :param name: file category
    :param suffix: a list, contains file suffixes
    """
    suffix = ["*." + re.sub(r'^[\*]*\.', '', s) for s in suffix]
    return f"{name} ({' '.join(suffix)})"


def joinFileCategories(categories: list):
    """
    concatenate multiple file filters for QFileDialog
    :param categories: QFileDialog format from setupOneFileCategory()
    """
    return ';;'.join(categories)
