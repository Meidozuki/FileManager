import logging
import sys

from PySide6.QtWidgets import (
    QApplication
)

from src import NavigatorWindow

if __name__ == '__main__':

    logging.getLogger('root').setLevel(logging.INFO)
    app = QApplication(sys.argv)

    # window = MainWindow()
    window = NavigatorWindow()
    window.show()

    app.exec()
