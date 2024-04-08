import os
import logging
import numpy as np
import pandas as pd
from typing import Optional, Tuple, List
from PIL import Image, ImageQt


from PySide6.QtWidgets import (
    QWidget, QPushButton, QLabel)
from PySide6.QtGui import QIcon, QPixmap, QImage, QStandardItem

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


class TableItemChecklist:
    class ItemRole:
        uncertain = None
        ModelRole = 'model'
        ViewRole = 'view'

    ModelRole = ItemRole.ModelRole
    ViewRole = ItemRole.ViewRole

    def __init__(self, name: str, col: int, role: ItemRole | str):
        self.name = name
        self.col = col
        self.role = role


class TableItem:
    def __init__(self, filename: str = None):
        super().__init__()

        self._filename = filename
        self._display = None
        self.image_size = (100, 100)
        self.tags = []

    def __str__(self):
        return f'TableItem("{self._filename}")'

    def recordMapping(self):
        mapping = {'filename': self._filename,
                   'display_image': self._display,
                   'tags': ', '.join(self.tags)}
        return mapping

    # save
    def toRecord(self):
        mapping = self.recordMapping()
        return pd.DataFrame(mapping.values(), mapping.keys()).T

    @classmethod
    def fromRecords(cls, data: pd.DataFrame):
        res = []
        for i in range(data.shape[0]):
            temp = TableItem()
            row = data.iloc[i]
            temp._filename = row['filename']
            temp.setDisplay(row['display_image'])
            temp.setTags(row['tags'])
            res.append(temp)
        return res

    # setter
    def setFilename(self, filename: str, *, force: bool = False):
        if os.path.exists(filename) or force:
            self._filename = filename
        else:
            logging.warning(f"You are trying to add a non-existing file {filename}")

    def setDisplay(self, display_filename: str | None) -> bool:
        if display_filename is None or not os.path.exists(display_filename):
            return False
        else:
            self._display = display_filename
            return True

    def setTags(self, tags):
        if tags is None or not isinstance(tags, (str, list)):
            return

        if not tags:
            self.tags = []
        else:
            self.tags = tags

    # getter
    @property
    def short_name(self):
        return os.path.split(self._filename)[1]

    @property
    def full_name(self):
        return os.path.abspath(self._filename)

    @property
    def icon(self) -> Optional[QIcon]:
        return getFileIcon(self._filename)

    def getPreviewImage(self) -> Optional[QPixmap]:
        if self._display is not None:
            pil_image = readImage(self._display, self.image_size)
            return ImageQt.toqpixmap(pil_image)
        else:
            return None

    # to table view
    @property
    def checklist(self) -> List[TableItemChecklist]:
        model_role, view_role = TableItemChecklist.ModelRole, TableItemChecklist.ViewRole
        ls = [
            TableItemChecklist('short_name_icon', 0, model_role),
            TableItemChecklist('preview', 1, view_role),
            TableItemChecklist('full_name', 2, model_role),
            TableItemChecklist('tags', 3, model_role),
            TableItemChecklist('icon', 4, model_role),
        ]
        return ls

    @property
    def expected_cols(self):
        return len(self.checklist)

    # etc
    def check(self) -> bool:
        if not os.path.exists(self._filename):
            return False
        if self._display is not None and not os.path.exists(self._display):
            return False

        return True
