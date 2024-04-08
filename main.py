import os, sys
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
from src import table_item, open_button, menu_bar, model


if __name__ == '__main__':
    # ls = [ [] for _ in range(10)]
    # for i in range(10):
    #     ls[i].append(i)
    #     ls[i].append(np.random.randint(10))
    # df = pd.DataFrame([ls]).T
    # print(df)
    # print(df[df[0].apply(lambda x: 4 in x)])


    app = QApplication(sys.argv)

    # t = model.Model()
    # df = t.load('temp/temp')
    # print(df)
    # print(df.shape)
    # print(table_item.TableItem.fromRecords(df))


    window = MainWindow()
    window.show()

    app.exec()
