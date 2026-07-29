import os
from typing import List, Optional, Union, Tuple

from PySide6.QtCore import QSize, Qt, Slot, QFileInfo, QModelIndex
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QMenuBar, QMenu,
    QWidget, QPushButton, QLabel, QFileIconProvider, QFileDialog, QInputDialog, QDialog,
    QMessageBox, QSplitter, QTableWidget, QTableWidgetItem, QHeaderView, QTableView,
    QAbstractItemView)
from PySide6.QtGui import (
    QIcon, QPixmap, QImage, QAction, QStandardItemModel, QStandardItem,
)

from .vbao_wrapper import vbao
from .viewmodel import ViewModel
from .ui import MenuBar, createQuickButtons
from .table_item import TableItem
from .tag.panel import TagManagerDialog, TagPanel


class MainWindow(QMainWindow, vbao.core.View):
    def __init__(self):
        super().__init__()

        self.prop_listener = ViewPropListener(self)
        self.cmd_listener = ViewCmdListener(self)

        self.setWindowTitle("File Manager")
        self.resize(QSize(1180, 720))

        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)

        self.viewmodel = ViewModel()
        self.view = QTableView()
        self.setupTableView()
        self.tag_panel = TagPanel(self)
        self.tag_manager_dialog = None
        self.setupTagPanel()

        self.layout_widget = self.createTableLayout()
        self.setCentralWidget(self.layout_widget)

        vbao.core.App.bind(self.viewmodel.model, self.viewmodel, self, True)
        self.viewmodel.init()
        self.refreshTagPanel()

    @property
    def selectedIndexes(self) -> set:
        return set([i.row() for i in self.view.selectedIndexes()])

    @property
    def selectedOneRow(self) -> Union[bool, Tuple[bool, int]]:
        """
        return only False when invalid, to simplify if statement
        """
        if len(self.selectedIndexes) != 1:
            return False
        else:
            return True, list(self.selectedIndexes)[0]

    @property
    def selectedOneSourceIndex(self) -> Union[bool, Tuple[bool, int]]:
        selected = self.selectedOneRow
        if not selected:
            return False
        try:
            return True, self.viewmodel.sourceIndexForViewRow(selected[1])
        except IndexError:
            return False

    @property
    def save_format(self):
        return self.getProperty('save_format')

    @property
    def temp_dir(self):
        return self.getProperty("temp_dir")

    def getIndex(self, i, j):
        return self.view.model().index(i, j)

    def setIndexWidget(self, i, j, widget: Optional[QWidget]):
        self.view.setIndexWidget(self.getIndex(i, j), widget)

    def setupTableView(self):
        self.view.setModel(self.viewmodel)

        self.view.setIconSize(QSize(30, 30))

        header_view = QHeaderView(Qt.Orientation.Vertical, None)
        header_view.setDefaultSectionSize(100)
        self.view.setVerticalHeader(header_view)

        self.view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.view.selectionModel().selectionChanged.connect(self.onTableSelectionChanged)

    def setupTagPanel(self):
        self.tag_panel.filterChanged.connect(self.commandApplyTagFilter)
        self.tag_panel.clearFilterRequested.connect(self.commandClearTagFilter)
        self.tag_panel.fileTagChanged.connect(self.commandToggleCurrentFileTag)
        self.tag_panel.manageRequested.connect(self.commandOpenTagManager)

    def _selectedTableItem(self) -> Optional[TableItem]:
        selected = self.selectedOneRow
        if not selected:
            return None
        try:
            return self.viewmodel.itemForViewRow(selected[1])
        except IndexError:
            return None

    def refreshTagPanel(self):
        item = self._selectedTableItem()
        items = self.getProperty_vbao("item_list") or []
        self.tag_panel.setState(
            self.viewmodel.tag_model,
            self.viewmodel.tag_filter,
            item.short_name if item is not None else None,
            item.tags if item is not None else [],
            len(self.viewmodel.visible_source_indices),
            len(items),
        )
        if self.tag_manager_dialog is not None:
            self.tag_manager_dialog.setTagModel(self.viewmodel.tag_model)

    @Slot()
    def onTableSelectionChanged(self, *args):
        item = self._selectedTableItem()
        self.tag_panel.setCurrentFile(
            item.short_name if item is not None else None,
            item.tags if item is not None else [],
        )

    def updateData(self):
        items = self.getProperty("item_list")
        for view_row, source_index in enumerate(self.viewmodel.visible_source_indices):
            self.setIndexWidget(view_row, 1, None)
            row_data = items[source_index]
            pixmap = row_data.getPreviewImage()
            if pixmap is not None:
                preview_image = QLabel()
                preview_image.setPixmap(pixmap)
                self.setIndexWidget(view_row, 1, preview_image)
            else:
                self.viewmodel.setItem(view_row, 1, QStandardItem("None"))

    def createTableLayout(self):
        """setLayout() will auto parent"""
        parent = QWidget(self)

        outer_v = QVBoxLayout()

        inner_h = createQuickButtons(self)
        label = QLabel("Current directory: ")
        label.setObjectName("work dir display")

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(self.view)
        splitter.addWidget(self.tag_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        splitter.setSizes([850, 330])

        outer_v.addLayout(inner_h)
        outer_v.addWidget(splitter)
        outer_v.addWidget(label)

        parent.setLayout(outer_v)
        return parent

    # button slots
    @Slot()
    def testFn(self):
        print('test fn')
        widget = QDialog(self)
        widget.exec_()

    @Slot()
    def commandOpenFolder(self):
        selected = self.selectedOneRow
        if selected:
            try:
                item = self.viewmodel.itemForViewRow(selected[1])
            except IndexError:
                return
            path = os.path.dirname(item.abs_path)
            self.getCommand("open").directCall('powershell', 'start ' + path)

    @Slot()
    def commandOpenFile(self):
        selected = self.selectedOneRow
        if selected:
            try:
                item = self.viewmodel.itemForViewRow(selected[1])
            except IndexError:
                return
            self.getCommand("open").directCall('powershell', 'start ' + item.abs_path)

    @Slot()
    def commandAddNewFiles(self):
        # [from doc] If parent is not None, the dialog will be shown centered over the parent widget.
        names, category = QFileDialog.getOpenFileNames(None, "Select files to add")

        if names:
            for name in names:
                self.getCommand("add_file").directCall(name)

    @Slot()
    def commandUpdateImage(self):
        rows = self.selectedOneRow
        if rows:
            name, category = QFileDialog.getOpenFileName(None, "Select preview image")
            if name:
                self.getCommand("update_image").directCall(rows[1], name)

    @Slot()
    def commandSetTags(self):
        rows = self.selectedOneRow
        if rows:
            item = self._selectedTableItem()
            tags, ok = QInputDialog.getText(
                self,
                "设置 Tag",
                "请输入以逗号分隔的 Tag",
                text=item.tags_text if item is not None else "",
            )
            if ok:
                self.getCommand("update_tags").directCall(rows[1], tags)

    @Slot(object, object)
    def commandApplyTagFilter(self, exclusive, coexist):
        self.getCommand("filter_tags").directCall(exclusive, coexist)

    @Slot()
    def commandClearTagFilter(self):
        self.runCommand("clear_filters")

    @Slot(str, bool)
    def commandToggleCurrentFileTag(self, tag: str, selected: bool):
        rows = self.selectedOneRow
        if rows:
            self.getCommand("toggle_file_tag").directCall(rows[1], tag, selected)

    @Slot()
    def commandOpenTagManager(self):
        if self.tag_manager_dialog is not None:
            self.tag_manager_dialog.raise_()
            self.tag_manager_dialog.activateWindow()
            return
        dialog = TagManagerDialog(self.viewmodel.tag_model, self)
        dialog.operationRequested.connect(self.commandManageTagDefinition)
        self.tag_manager_dialog = dialog
        try:
            dialog.exec()
        finally:
            self.tag_manager_dialog = None

    @Slot(str, object)
    def commandManageTagDefinition(self, action: str, payload):
        self.getCommand("manage_tags").directCall(action, *tuple(payload))


class ViewPropListener(vbao.PropertyListenerBase):
    def onPropertyChanged(self, prop_name: str):
        match prop_name:
            case 'items':
                self.master.updateData()
                self.master.refreshTagPanel()
            case 'tag_schema':
                self.master.refreshTagPanel()
            case 'tag_error':
                message = self.master.getProperty("tag_error")
                if message:
                    QMessageBox.warning(self.master, "操作失败", message)
            case 'work_dir':
                label = self.master.layout_widget.findChild(QLabel, "work dir display")
                label.setText("Current directory: " + self.master.getProperty("work_dir"))
            case _:
                print('uncaught prop ' + prop_name)


class ViewCmdListener(vbao.CommandListenerBase):
    def onCommandComplete(self, cmd_name: str, success: bool):
        print(f"Command {cmd_name} success:{success}")
        match cmd_name:
            case 'clear':
                self.master.view.reset()
