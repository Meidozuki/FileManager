import os, sys
import logging
from typing import *

import numpy as np
import pandas as pd
from abc import ABC

from PySide6.QtCore import QSize, Qt, Slot, QFileInfo
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QMenuBar, QMenu,
    QWidget, QPushButton, QLabel, QFileIconProvider,QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QTableView, QListView, QTreeView)
from PySide6.QtGui import (
    QIcon, QPixmap, QImage, QAction, QStandardItemModel
)

from src import MainWindow, vbao
from src import table_item, model, vm_commands


if __name__ == '__main__':

    logging.getLogger('root').setLevel(logging.INFO)
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
