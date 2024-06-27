import os
import logging
from glob import glob

from PySide6.QtCore import QSize, Qt, Slot, QFileInfo, QModelIndex
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QMenuBar, QMenu, QSizePolicy,
    QWidget, QPushButton, QLabel, QFileIconProvider, QFileDialog, QInputDialog, QDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QTableView, QAbstractItemView, QCheckBox)
from PySide6.QtGui import (
    QIcon, QPixmap, QImage, QAction, QStandardItemModel, QStandardItem,
)

from ui.ui_ren_suf import Ui_RenameSuffixWindow

_default_options = {
    'enabled': False,
    'append': True,
    'empty': False,
}

_key_mapping = {
    'enabled': 'enabled',
    'append': u'后缀附加而不是替换',
    'empty': u'此框是个装饰'
}


class KeyTranslationHelper:
    @classmethod
    def get(cls, key):
        return _key_mapping[key] if key in _key_mapping else key


class WindowRenameSuffix(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_RenameSuffixWindow()
        self.ui.setupUi(self)

        # current folder
        self._cur_dir = ''
        self.curdir_label = self.ui.curdir_label
        self.set_dir(os.path.abspath(os.curdir))
        self.ui.chdir_button.clicked.connect(self.select_folder)

        # options
        self.option_layout = self.ui.option_layout
        # delete the placeholder
        temp = self.ui.layout_widget.findChild(QCheckBox, 'placeholder')
        self.ui.option_layout.removeWidget(temp)
        temp.deleteLater()
        # add options
        for key in _default_options:
            box = self.create_check_box(key)
            self.option_layout.addWidget(box)

        # table
        self.table = self.ui.table
        self.setup_table_view()
        self.ui.exec_button.clicked.connect(self.rename_logic)
        print(self.logic_arguments)

    def set_dir(self, new_dir: str):
        if os.path.exists(new_dir):
            self._cur_dir = os.path.normpath(new_dir)
            self.curdir_label.setText(self._cur_dir)
        else:
            logging.warning(f"[RenameSuffix] chdir to a non-existing path {new_dir}")

    @Slot()
    def select_folder(self):
        new_dir = QFileDialog.getExistingDirectory(self)
        if new_dir:
            self.set_dir(new_dir)

    def create_check_box(self, key) -> QCheckBox:
        checkbox = QCheckBox(self)
        checkbox.setObjectName(key)
        checkbox.setText(KeyTranslationHelper.get(key))
        checkbox.setChecked(_default_options[key])
        return checkbox

    def setup_table_view(self):
        self.table.setHorizontalHeaderLabels(['old name', 'new name'])
        header = self.table.horizontalHeader()
        # header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        # header.setStretchLastSection(True)
        # 设置默认列宽由于拿不到现在的大小，所以在Designer中设置
        # 可以考虑继承TableWidget重写resizeEvent，但现在足够用了

    def on_rename_failed(self):
        self.table.clearContents()
        self.table.setRowCount(1)
        self.table.setItem(0, 0, QTableWidgetItem("Invalid regex pattern!"))

    @property
    def logic_arguments(self):
        d = {}
        d['append'] = self.findChild(QCheckBox, 'append').isChecked()
        d['dry_run'] = not self.findChild(QCheckBox, 'enabled').isChecked()
        return d

    @Slot()
    def rename_logic(self):
        def change_suffix(path, suffix, append=True, *, dry_run=True):
            assert os.path.exists(path)
            # 后缀名保持.xxx格式，除了空后缀不需要.
            suffix = '.' + suffix.replace('.', '') if suffix else ''

            # 文件夹的后缀无意义
            if os.path.isdir(path): return

            prefix, ext = os.path.splitext(path)
            # 已经同后缀，短路
            if ext == suffix: return

            # 空后缀强制append
            if ext == '' or append:
                new_name = path + suffix
            else:
                new_name = prefix + suffix

            if not dry_run:
                os.rename(path, new_name)
            return new_name

        old_pat = self.ui.old_pattern.toPlainText()
        new_pat = self.ui.new_pattern.toPlainText()
        print(f"Try to rename pattern '{old_pat}' to '{new_pat}' under folder {self._cur_dir}")

        # 未输入时不工作
        # 禁止向上目录
        if not old_pat or old_pat.find('..') != -1:
            self.on_rename_failed()
            return

        files = glob(os.path.join(self._cur_dir, old_pat))
        n = len(files)
        self.table.clearContents()
        self.table.setRowCount(n)

        for i in range(n):
            old, new = files[i], change_suffix(files[i], new_pat, **self.logic_arguments)
            self.table.setItem(i, 0, QTableWidgetItem(old))
            self.table.setItem(i, 1, QTableWidgetItem(new))
