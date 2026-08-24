import os
from typing import Optional, Union, Tuple

from PySide6.QtCore import QSize, Qt, Slot
from PySide6.QtGui import (
    QStandardItem,
)
from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QFileDialog, QInputDialog,
    QMessageBox, QSplitter, QAbstractItemView, QFrame, QStackedWidget, QSizePolicy)

from views.table_view import FileTableView
from .table_item import TableItem
from .tag.panel import TagManagerDialog, TagPanel
from .theme import MAIN_WINDOW_STYLE
from .ui import MenuBar, createQuickButtons
from .vbao_wrapper import vbao
from .viewmodel import ViewModel


class ElidedLabel(QLabel):
    def __init__(self, text: str = "", parent=None):
        super().__init__(parent)
        self._full_text = ""
        self.setFullText(text)

    @property
    def fullText(self) -> str:
        return self._full_text

    def setFullText(self, text: str):
        self._full_text = text or ""
        self.setToolTip(self._full_text)
        self._update_elided_text()

    def _update_elided_text(self):
        available_width = max(0, self.contentsRect().width())
        elided = self.fontMetrics().elidedText(
            self._full_text,
            Qt.TextElideMode.ElideMiddle,
            available_width,
        )
        super().setText(elided)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_elided_text()


class MainWindow(QMainWindow, vbao.core.View):
    def __init__(self):
        super().__init__()

        self.prop_listener = ViewPropListener(self)
        self.cmd_listener = ViewCmdListener(self)

        # self.setObjectName("mainWindow")
        self.setWindowTitle("文件管理器")
        self.resize(QSize(1180, 720))
        # self.setMinimumSize(QSize(880, 560))
        self.setStyleSheet(MAIN_WINDOW_STYLE)

        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)

        self.viewmodel = ViewModel()
        self.view = None
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
        self.view = FileTableView(self.viewmodel)

        self.view.setIconSize(QSize(30, 30))
        self.view.setAlternatingRowColors(True)
        # self.view.setShowGrid(False)
        # self.view.setWordWrap(False)
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
        visible_count = len(self.viewmodel.visible_source_indices)
        total_count = len(items)
        self.tag_panel.setState(
            self.viewmodel.tag_model,
            self.viewmodel.tag_filter,
            item.short_name if item is not None else None,
            item.tags if item is not None else [],
            visible_count,
            total_count,
        )
        if hasattr(self, "status_count_label"):
            self.status_count_label.setText(f"显示 {visible_count} / 共 {total_count}")
        if hasattr(self, "empty_state") and hasattr(self, "table_stack"):
            if visible_count:
                self.table_stack.setCurrentWidget(self.view)
            else:
                self.empty_state.setText(
                    "还没有文件，点击“添加文件”开始整理。"
                    if total_count == 0
                    else "没有符合当前 Tag 筛选条件的文件。"
                )
                self.table_stack.setCurrentWidget(self.empty_state)
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
                preview_image.setObjectName("previewImage")
                preview_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
                preview_image.setPixmap(pixmap)
                self.setIndexWidget(view_row, 1, preview_image)
            else:
                empty_preview = QStandardItem("无预览")
                empty_preview.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.viewmodel.setItem(view_row, 1, empty_preview)

    def createTableLayout(self):
        parent = QWidget(self)
        parent.setObjectName("mainContent")
        outer_v = QVBoxLayout(parent)
        outer_v.setContentsMargins(16, 14, 16, 14)
        outer_v.setSpacing(12)

        toolbar_card = QFrame(parent)
        toolbar_card.setObjectName("toolBarCard")
        toolbar_card.setLayout(createQuickButtons(self))
        outer_v.addWidget(toolbar_card)

        table_card = QFrame(parent)
        table_card.setObjectName("tableCard")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        table_header = QWidget(table_card)
        table_header_layout = QHBoxLayout(table_header)
        table_header_layout.setContentsMargins(14, 11, 14, 10)
        title_block = QVBoxLayout()
        title_block.setSpacing(1)
        title = QLabel("文件列表")
        title.setObjectName("workspaceTitle")
        subtitle = QLabel("浏览文件、预览图与 Tag 信息")
        subtitle.setObjectName("workspaceSubtitle")
        title_block.addWidget(title)
        title_block.addWidget(subtitle)
        table_header_layout.addLayout(title_block)
        table_header_layout.addStretch()
        table_layout.addWidget(table_header)

        self.table_stack = QStackedWidget(table_card)
        self.table_stack.setObjectName("tableStack")
        self.empty_state = QLabel("还没有文件，点击“添加文件”开始整理。")
        self.empty_state.setObjectName("emptyState")
        self.empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_state.setWordWrap(True)
        self.table_stack.addWidget(self.view)
        self.table_stack.addWidget(self.empty_state)
        table_layout.addWidget(self.table_stack)

        splitter = QSplitter(Qt.Orientation.Horizontal, parent)
        splitter.setObjectName("workspaceSplitter")
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(7)
        splitter.addWidget(table_card)
        splitter.addWidget(self.tag_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        splitter.setSizes([850, 330])
        outer_v.addWidget(splitter, 1)

        status_card = QFrame(parent)
        status_card.setObjectName("statusCard")
        status_layout = QHBoxLayout(status_card)
        status_layout.setContentsMargins(12, 7, 12, 7)
        status_layout.setSpacing(8)
        caption = QLabel("当前目录")
        caption.setObjectName("statusCaption")
        self.work_dir_label = ElidedLabel("尚未设置")
        self.work_dir_label.setObjectName("work dir display")
        self.work_dir_label.setMinimumWidth(80)
        self.work_dir_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )
        self.status_count_label = QLabel("显示 0 / 共 0")
        self.status_count_label.setObjectName("itemCountBadge")
        status_layout.addWidget(caption)
        status_layout.addWidget(self.work_dir_label, 1)
        status_layout.addWidget(self.status_count_label)
        outer_v.addWidget(status_card)

        return parent

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
                work_dir = self.master.getProperty("work_dir") or "尚未设置"
                if isinstance(label, ElidedLabel):
                    label.setFullText(work_dir)
                elif label is not None:
                    label.setText(work_dir)
                    label.setToolTip(work_dir)
            case _:
                print('uncaught prop ' + prop_name)


class ViewCmdListener(vbao.CommandListenerBase):
    def onCommandComplete(self, cmd_name: str, success: bool):
        print(f"Command {cmd_name} success:{success}")
        match cmd_name:
            case 'clear':
                self.master.view.reset()
