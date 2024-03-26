import os, sys
from typing import *
from PIL import Image, ImageQt

from PySide6.QtCore import QSize, Qt, Slot, QFileInfo
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QMenuBar, QMenu,
    QWidget, QPushButton, QLabel, QFileIconProvider,QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QTableView)
from PySide6.QtGui import (
    QIcon, QPixmap, QImage, QAction, QStandardItemModel
)

from src import MainWindow
from src import table_item, open_button, menu_bar, model

import vbao



if __name__ == '__main__':
    # m = model.Model()
    # print(m.load('temp'))

    app = QApplication(sys.argv)

    # print(QFileDialog.getOpenFileNames(window))
    window = MainWindow()
    window.show()

    app.exec()
