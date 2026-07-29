import copy
import json

import pytest

from src.row_mapping import source_index_for_view_row
from src.tag import TagFilter, TagModel, TagRuleError, normalize_tags


def make_tag_model():
    model = TagModel()
    file_type = model.add_group("文件类型", "file-type")
    month = model.add_group("文件时间", "file-month")
    model.add_tag("图片", file_type.id)
    model.add_tag("视频", file_type.id)
    model.add_tag("26年1月", month.id)
    model.add_tag("26年2月", month.id)
    model.add_tag("收藏")
    model.add_tag("已审核")
    return model


def test_normalize_tags_removes_blank_and_duplicates():
    assert normalize_tags(" 图片, 收藏, 图片, ,已审核 ") == ["图片", "收藏", "已审核"]
    assert normalize_tags(None) == []
    with pytest.raises(TagRuleError):
        normalize_tags(["非法,Tag"])


def test_exclusive_selection_replaces_only_same_group():
    model = make_tag_model()
    original = ["图片", "26年1月", "收藏"]

    updated = model.apply_tag_selection(original, "视频", True)

    assert updated == ["26年1月", "收藏", "视频"]
    assert original == ["图片", "26年1月", "收藏"]
    assert model.validate_file_tags(updated) == []


def test_text_tag_edit_keeps_last_exclusive_value():
    model = make_tag_model()

    normalized = model.enforce_file_tags([
        "图片", "收藏", "视频", "26年1月", "26年2月", "已审核"
    ])

    assert normalized == ["收藏", "视频", "26年2月", "已审核"]
    assert model.validate_file_tags(normalized) == []


def test_filter_uses_exact_and_matching_without_mutating_records():
    records = [
        ["图片", "26年1月", "收藏"],
        ["视频", "26年1月", "收藏"],
        ["图片", "26年2月", "收藏"],
        ["图片", "26年1月", "已审核"],
        ["图片集", "26年1月", "收藏"],
    ]
    original = copy.deepcopy(records)
    tag_filter = TagFilter(
        {"file-type": "图片", "file-month": "26年1月"},
        ["收藏"],
    )

    visible_source_indices = [
        index for index, tags in enumerate(records)
        if tag_filter.matches(tags)
    ]

    assert visible_source_indices == [0]
    assert records == original


def test_empty_filter_matches_every_record():
    tag_filter = TagFilter()
    assert tag_filter.is_empty
    assert tag_filter.matches([])
    assert tag_filter.matches(["任意Tag"])


def test_runtime_definition_changes_update_rules_without_losing_group_tags():
    model = make_tag_model()
    model.rename_tag("收藏", "精选")
    assert "精选" in model.coexist_tags
    assert model.rename_in_file_tags(["图片", "收藏"], "收藏", "精选") == ["图片", "精选"]

    model.move_tag("精选", "file-type")
    assert model.apply_tag_selection(["视频", "精选"], "精选") == ["精选"]

    model.delete_group("file-type")
    assert {"图片", "视频", "精选"}.issubset(set(model.coexist_tags))

    model.delete_tag("精选")
    assert "精选" not in model.all_tags
    assert model.remove_from_file_tags(["图片", "精选"], "精选") == ["图片"]


def test_tag_schema_json_round_trip_and_old_metadata_compatibility():
    model = make_tag_model()
    metadata = {
        "work_dir": "D:/example",
        **model.to_dict(),
    }

    restored = TagModel.from_dict(json.loads(json.dumps(metadata, ensure_ascii=False)))

    assert restored.to_dict() == model.to_dict()

    old_metadata = {"work_dir": "D:/legacy"}
    old_model = TagModel.from_dict(old_metadata)
    old_model.register_existing_tags(["旧Tag", "图片"])
    assert old_model.exclusive_groups == []
    assert old_model.coexist_tags == ["旧Tag", "图片"]


def test_invalid_metadata_fields_fall_back_to_empty_schema():
    restored = TagModel.from_dict({
        "exclusive_groups": "not-a-list",
        "coexist_tags": 123,
    })
    assert restored.all_tags == []


def test_source_row_mapping_uses_visible_source_indices():
    mapping = [4, 7, 11]
    assert source_index_for_view_row(mapping, 0) == 4
    assert source_index_for_view_row(mapping, 2) == 11

    with pytest.raises(IndexError):
        source_index_for_view_row(mapping, -1)
    with pytest.raises(IndexError):
        source_index_for_view_row(mapping, 3)
    with pytest.raises(TypeError):
        source_index_for_view_row(mapping, "1")
    with pytest.raises(ValueError):
        source_index_for_view_row([2, -1], 1)
