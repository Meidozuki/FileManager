# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'rename_suffix_window.ui'
##
## Created by: Qt User Interface Compiler version 6.6.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QHBoxLayout, QHeaderView,
    QLabel, QLayout, QMainWindow, QMenu,
    QMenuBar, QPlainTextEdit, QPushButton, QSizePolicy,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_RenameSuffixWindow(object):
    def setupUi(self, RenameSuffixWindow):
        if not RenameSuffixWindow.objectName():
            RenameSuffixWindow.setObjectName(u"RenameSuffixWindow")
        RenameSuffixWindow.resize(800, 600)
        self.centralwidget = QWidget(RenameSuffixWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.layout_widget = QWidget(self.centralwidget)
        self.layout_widget.setObjectName(u"layout_widget")
        self.layout_widget.setGeometry(QRect(90, 30, 600, 501))
        self.vertical_layout = QVBoxLayout(self.layout_widget)
        self.vertical_layout.setObjectName(u"vertical_layout")
        self.regex_input_layout = QHBoxLayout()
        self.regex_input_layout.setObjectName(u"regex_input_layout")
        self.old_hint = QLabel(self.layout_widget)
        self.old_hint.setObjectName(u"old_hint")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.old_hint.sizePolicy().hasHeightForWidth())
        self.old_hint.setSizePolicy(sizePolicy)

        self.regex_input_layout.addWidget(self.old_hint)

        self.old_pattern = QPlainTextEdit(self.layout_widget)
        self.old_pattern.setObjectName(u"old_pattern")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.old_pattern.sizePolicy().hasHeightForWidth())
        self.old_pattern.setSizePolicy(sizePolicy1)
        self.old_pattern.setMaximumSize(QSize(16777215, 50))

        self.regex_input_layout.addWidget(self.old_pattern)

        self.new_hint = QLabel(self.layout_widget)
        self.new_hint.setObjectName(u"new_hint")
        sizePolicy.setHeightForWidth(self.new_hint.sizePolicy().hasHeightForWidth())
        self.new_hint.setSizePolicy(sizePolicy)

        self.regex_input_layout.addWidget(self.new_hint)

        self.new_pattern = QPlainTextEdit(self.layout_widget)
        self.new_pattern.setObjectName(u"new_pattern")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.new_pattern.sizePolicy().hasHeightForWidth())
        self.new_pattern.setSizePolicy(sizePolicy2)
        self.new_pattern.setMaximumSize(QSize(16777215, 50))
        self.new_pattern.setBaseSize(QSize(0, 0))

        self.regex_input_layout.addWidget(self.new_pattern)


        self.vertical_layout.addLayout(self.regex_input_layout)

        self.cur_dir_layout = QHBoxLayout()
        self.cur_dir_layout.setObjectName(u"cur_dir_layout")
        self.cur_dir_layout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.curdir_hint = QLabel(self.layout_widget)
        self.curdir_hint.setObjectName(u"curdir_hint")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.curdir_hint.sizePolicy().hasHeightForWidth())
        self.curdir_hint.setSizePolicy(sizePolicy3)

        self.cur_dir_layout.addWidget(self.curdir_hint)

        self.curdir_label = QLabel(self.layout_widget)
        self.curdir_label.setObjectName(u"curdir_label")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.curdir_label.sizePolicy().hasHeightForWidth())
        self.curdir_label.setSizePolicy(sizePolicy4)

        self.cur_dir_layout.addWidget(self.curdir_label)

        self.chdir_button = QPushButton(self.layout_widget)
        self.chdir_button.setObjectName(u"chdir_button")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.chdir_button.sizePolicy().hasHeightForWidth())
        self.chdir_button.setSizePolicy(sizePolicy5)

        self.cur_dir_layout.addWidget(self.chdir_button)


        self.vertical_layout.addLayout(self.cur_dir_layout)

        self.option_layout = QHBoxLayout()
        self.option_layout.setObjectName(u"option_layout")
        self.option_hint = QLabel(self.layout_widget)
        self.option_hint.setObjectName(u"option_hint")
        sizePolicy3.setHeightForWidth(self.option_hint.sizePolicy().hasHeightForWidth())
        self.option_hint.setSizePolicy(sizePolicy3)

        self.option_layout.addWidget(self.option_hint)

        self.placeholder = QCheckBox(self.layout_widget)
        self.placeholder.setObjectName(u"placeholder")

        self.option_layout.addWidget(self.placeholder)


        self.vertical_layout.addLayout(self.option_layout)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.hint_label = QLabel(self.layout_widget)
        self.hint_label.setObjectName(u"hint_label")
        sizePolicy3.setHeightForWidth(self.hint_label.sizePolicy().hasHeightForWidth())
        self.hint_label.setSizePolicy(sizePolicy3)

        self.horizontalLayout.addWidget(self.hint_label)

        self.hint_text = QLabel(self.layout_widget)
        self.hint_text.setObjectName(u"hint_text")

        self.horizontalLayout.addWidget(self.hint_text)


        self.vertical_layout.addLayout(self.horizontalLayout)

        self.exec_button = QPushButton(self.layout_widget)
        self.exec_button.setObjectName(u"exec_button")

        self.vertical_layout.addWidget(self.exec_button)

        self.table = QTableWidget(self.layout_widget)
        if (self.table.columnCount() < 2):
            self.table.setColumnCount(2)
        if (self.table.rowCount() < 1):
            self.table.setRowCount(1)
        self.table.setObjectName(u"table")
        self.table.setRowCount(1)
        self.table.setColumnCount(2)
        self.table.horizontalHeader().setDefaultSectionSize(250)
        self.table.horizontalHeader().setStretchLastSection(True)

        self.vertical_layout.addWidget(self.table)

        RenameSuffixWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(RenameSuffixWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 21))
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        RenameSuffixWindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(RenameSuffixWindow)

        QMetaObject.connectSlotsByName(RenameSuffixWindow)
    # setupUi

    def retranslateUi(self, RenameSuffixWindow):
        RenameSuffixWindow.setWindowTitle(QCoreApplication.translate("RenameSuffixWindow", u"RenameSuffix", None))
        self.old_hint.setText(QCoreApplication.translate("RenameSuffixWindow", u"Old:", None))
        self.new_hint.setText(QCoreApplication.translate("RenameSuffixWindow", u"New:", None))
        self.curdir_hint.setText(QCoreApplication.translate("RenameSuffixWindow", u"Cur Dir: ", None))
        self.curdir_label.setText(QCoreApplication.translate("RenameSuffixWindow", u"curdir_example", None))
        self.chdir_button.setText(QCoreApplication.translate("RenameSuffixWindow", u"chdir", None))
        self.option_hint.setText(QCoreApplication.translate("RenameSuffixWindow", u"Options: ", None))
        self.placeholder.setText(QCoreApplication.translate("RenameSuffixWindow", u"enabled", None))
        self.hint_label.setText(QCoreApplication.translate("RenameSuffixWindow", u"Tips: ", None))
        self.hint_text.setText(QCoreApplication.translate("RenameSuffixWindow", u"Text", None))
        self.exec_button.setText(QCoreApplication.translate("RenameSuffixWindow", u"Run", None))
        self.menuHelp.setTitle(QCoreApplication.translate("RenameSuffixWindow", u"Help", None))
    # retranslateUi

