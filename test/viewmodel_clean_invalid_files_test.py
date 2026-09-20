import os

import pytest

pytest.importorskip("numpy")
pytest.importorskip("pandas")
pytest.importorskip("PIL")
pytest.importorskip("PySide6")

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from src.table_item import TableItem
from src.viewmodel import ViewModel


@pytest.fixture(scope="module", autouse=True)
def qt_application():
    app = QApplication.instance() or QApplication([])
    yield app


def make_viewmodel(tmp_path, items):
    viewmodel = ViewModel()
    viewmodel.model.config["auto_show_image_file"] = False
    viewmodel.setProperty_vbao("work_dir", str(tmp_path))
    viewmodel.setProperty_vbao("item_list", items)
    viewmodel.onDataChanged()
    return viewmodel


def make_item(tmp_path, name, tags):
    item = TableItem(str(tmp_path / name))
    item.setTags(tags)
    return item


def test_clean_invalid_files_removes_missing_items_with_mocked_exists(tmp_path, monkeypatch):
    items = [
        make_item(tmp_path, "keep-a.jpg", ["图片"]),
        make_item(tmp_path, "missing.mp4", ["视频"]),
        make_item(tmp_path, "keep-b.png", ["收藏"]),
    ]
    viewmodel = make_viewmodel(tmp_path, items)

    kept_paths = {items[0].abs_path, items[2].abs_path}

    def fake_exists(path):
        return path in kept_paths

    monkeypatch.setattr("src.viewmodel.os.path.exists", fake_exists)

    viewmodel.cleanInvalidFiles()

    remained = viewmodel.getProperty_vbao("item_list")
    assert [item.short_name for item in remained] == ["keep-a.jpg", "keep-b.png"]
    assert viewmodel.visible_source_indices == [0, 1]
