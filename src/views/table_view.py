
from dataclasses import dataclass

from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QTableView, QHeaderView, QAbstractItemView


@dataclass
class HorizontalHeaderConfig:
    label: str
    width: int
    resize_mode: QHeaderView.ResizeMode = QHeaderView.ResizeMode.Interactive


class FileTableView(QTableView):
    def __init__(self, item_model: QStandardItemModel, *args, **kwargs):
        super().__init__(*args, **kwargs)

        ResizeMode = QHeaderView.ResizeMode
        self.configs = [
            HorizontalHeaderConfig("文件名",   220, ResizeMode.Interactive),
            HorizontalHeaderConfig("预览",     120, ResizeMode.Fixed),
            HorizontalHeaderConfig("标签",     180, ResizeMode.Interactive),
            HorizontalHeaderConfig("相对路径",  220, ResizeMode.Interactive),
            HorizontalHeaderConfig("绝对路径",  220, ResizeMode.Stretch),
        ]
        
        self.setModel(item_model)
        item_model.setHorizontalHeaderLabels([it.label for it in self.configs])

        self.setup_horizontal_header()
        self.setup_vertical_header()
        self.setup_scroll_mode()
        
    def setup_horizontal_header(self):
        header = self.horizontalHeader()
        header.setMinimumHeight(38)
        header.setStretchLastSection(True)
        
        for i, config in enumerate(self.configs):
            header.setSectionResizeMode(i, config.resize_mode)
            self.setColumnWidth(i, config.width)
        
    def setup_vertical_header(self):
        header = self.verticalHeader()
        header.setDefaultSectionSize(100)
        
    def setup_scroll_mode(self):
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
