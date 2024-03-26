import os
import logging
import pandas as pd
from typing import Optional, Tuple
from PIL import Image, ImageQt

assert ImageQt.qt_is_installed

from PySide6.QtWidgets import (
    QWidget, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, )
from PySide6.QtGui import QIcon, QPixmap, QImage

from .open_button import FileOpenButton
from .common import getFileIcon


def readImage(filename: str, size: Optional[Tuple[int, int]] = None):
    """
    will log an error if file not exist
    :param filename:
    :param size: optional
    :return:
    """
    if os.path.exists(filename):
        with Image.open(filename) as img:
            if size is not None:
                img = img.resize(size)
            return img.copy()
    else:
        logging.error(f"File not exist: {filename}")
        return None


class TableItem:
    def __init__(self, filename: str = None):
        super().__init__()

        self._filename = filename
        self._display = None
        self.image_size = (100, 100)
        self.tags = []

    # save
    def toRecord(self):
        mapping = {'filename': self._filename,
                   'display_image': self._display,
                   'tags': ', '.join(self.tags)}
        return pd.DataFrame(mapping.values(), mapping.keys()).T

    # setter
    def setFilename(self, filename: str, *, force: bool = False):
        if os.path.exists(filename) or force:
            self._filename = filename
        else:
            logging.warning(f"You are trying to add a non-existing file {filename}")

    def setDisplay(self, display_filename: str):
        if os.path.exists(display_filename):
            self._display = display_filename
        else:
            raise FileNotFoundError(display_filename)

    # getter
    def getShortName(self):
        return os.path.split(self._filename)[1]

    def getPreviewImage(self) -> Optional[QPixmap]:
        if self._display is not None:
            pil_image = readImage(self._display, self.image_size)
            return ImageQt.toqpixmap(pil_image)
        else:
            return None

    def getPreviewTableItem(self):
        item = QTableWidgetItem()
        if self._display is not None:
            item.setBackground(self.getPreviewImage())
        else:
            item.setText("None")
        return item

    def getOpenButton(self):
        button = FileOpenButton()
        button.setOverload(self._filename)
        return button

    # to table view
    def setupTableView(self):
        """
        This function is extracted for convenience when testing
        """
        self.viewer = {'short_name': lambda: QTableWidgetItem(self.getShortName()),
                       'full_name': lambda: QTableWidgetItem(os.path.abspath(self._filename)),
                       'preview': self.getPreviewTableItem,
                       'open_button': self.getOpenButton,
                       'icon': lambda: QTableWidgetItem(getFileIcon(self._filename), '')
                       }

        # immediately throw KeyError if not match
        self.pick = ['short_name', 'preview', 'open_button', 'full_name', 'icon']

    def toTableWidgetItems(self, *, auto_setup=True):
        assert self.check()

        if auto_setup:
            self.setupTableView()

        res = []
        for k in self.pick:
            item = self.viewer[k]()
            res.append(item)

            # check ahead of time
            if not isinstance(item, (QTableWidgetItem, QPushButton)):
                logging.warning(f'[getTableWidgetItems] '
                                f'The item {k} is not a valid candidate, may throw error afterwards')

        return res

    # etc
    def check(self) -> bool:
        if not os.path.exists(self._filename):
            return False
        if self._display is not None and not os.path.exists(self._display):
            return False

        return True
