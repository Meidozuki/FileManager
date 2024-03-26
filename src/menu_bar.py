from functools import wraps

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QMenuBar, QMenu,
    QWidget, QPushButton, QLabel)
from PySide6.QtGui import QIcon, QPixmap, QImage, QAction



class MenuBar(QMenuBar):
    @wraps(QMenuBar.__init__)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.constructTableOpMenu()


    def constructTableOpMenu(self):
        menu = QMenu(u"Table Op", self)
        menu.setObjectName(u"Table Op")
        self.addMenu(menu)

        # sub1 = QAction(menu1)
        # sub1.setText("sub1")
        sub1 = QAction(u"sub1", menu)
        sub1.setObjectName(u"sub1")
        sub1.ActionEvent
        menu.addAction(sub1)
