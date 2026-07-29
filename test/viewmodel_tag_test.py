import json
import os

import pytest

pytest.importorskip("numpy")
pytest.importorskip("pandas")
pytest.importorskip("PIL")
pytest.importorskip("PySide6")

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from src.table_item import TableItem
from src.tag import TagModel
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


def make_schema():
    schema = TagModel()
    group = schema.add_group("文件类型", "file-type")
    schema.add_tag("图片", group.id)
    schema.add_tag("视频", group.id)
    schema.add_tag("收藏")
    return schema


def test_filtered_edit_uses_source_row_without_replacing_source_data(tmp_path):
    items = [
        make_item(tmp_path, "video.mp4", ["视频", "收藏"]),
        make_item(tmp_path, "image-a.jpg", ["图片"]),
        make_item(tmp_path, "image-b.jpg", ["图片", "收藏"]),
    ]
    original_ids = [id(item) for item in items]
    viewmodel = make_viewmodel(tmp_path, items)
    viewmodel.tag_model = make_schema()

    viewmodel.setTagFilter({"file-type": "图片"}, ["收藏"])

    assert viewmodel.visible_source_indices == [2]
    assert viewmodel.sourceIndexForViewRow(0) == 2
    assert [id(item) for item in viewmodel.getProperty_vbao("item_list")] == original_ids

    viewmodel.updateTags(0, "视频, 收藏")

    assert items[0].tags == ["视频", "收藏"]
    assert items[1].tags == ["图片"]
    assert items[2].tags == ["视频", "收藏"]
    assert viewmodel.visible_source_indices == []
    assert [id(item) for item in viewmodel.getProperty_vbao("item_list")] == original_ids


def test_structured_filter_requires_every_selected_tag(tmp_path):
    items = [
        make_item(tmp_path, "a.jpg", ["图片", "收藏"]),
        make_item(tmp_path, "b.jpg", ["图片"]),
        make_item(tmp_path, "c.mp4", ["视频", "收藏"]),
    ]
    viewmodel = make_viewmodel(tmp_path, items)
    viewmodel.tag_model = make_schema()

    viewmodel.setTagFilter({"file-type": "图片"}, ["收藏"])

    assert viewmodel.visible_source_indices == [0]
    assert len(viewmodel.getProperty_vbao("item_list")) == 3


def test_viewmodel_csv_and_tag_schema_round_trip(tmp_path):
    items = [
        make_item(tmp_path, "a.jpg", ["图片", "收藏"]),
        make_item(tmp_path, "b.mp4", ["视频"]),
    ]
    csv_path = tmp_path / "records.csv"
    source = make_viewmodel(tmp_path, items)
    source.tag_model = make_schema()

    source.saveData(str(csv_path))

    metadata = json.loads((tmp_path / "records.json").read_text(encoding="utf-8"))
    assert metadata["work_dir"] == str(tmp_path)
    assert metadata["exclusive_groups"][0]["tags"] == ["图片", "视频"]
    assert metadata["coexist_tags"] == ["收藏"]
    assert "filter" not in metadata

    restored = make_viewmodel(tmp_path, [])
    restored.loadData(str(csv_path))
    restored_items = restored.getProperty_vbao("item_list")

    assert [item.tags for item in restored_items] == [
        ["图片", "收藏"],
        ["视频"],
    ]
    assert restored.tag_model.to_dict() == source.tag_model.to_dict()
    assert restored.tag_filter.is_empty


def test_loading_csv_without_schema_registers_existing_tags_as_coexist(tmp_path):
    items = [make_item(tmp_path, "legacy.jpg", ["旧Tag", "收藏"])]
    csv_path = tmp_path / "legacy.csv"
    source = make_viewmodel(tmp_path, items)
    source.model.save(items, str(csv_path))
    source.model.saveMetadata(str(csv_path), {"work_dir": str(tmp_path)})

    restored = make_viewmodel(tmp_path, [])
    restored.loadData(str(csv_path))

    assert restored.tag_model.exclusive_groups == []
    assert restored.tag_model.coexist_tags == ["旧Tag", "收藏"]
