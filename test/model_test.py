import json
import os, sys
import pytest

np = pytest.importorskip("numpy")
pd = pytest.importorskip("pandas")
pytest.importorskip("PIL")
pytest.importorskip("PySide6")

sys.path.append(os.path.abspath('..'))

from src.model import Model, TableItem

model = Model()

items = [TableItem(f'{i}.jpg') for i in range(10)]


def makeOneLineDf(cols, data=None):
    if data is None:
        data = range(len(cols))

    return pd.DataFrame(np.expand_dims(data, 0), columns=cols)


def test_item2df_shape():
    for i in range(1, 11):
        df = model.changeItemToDf(items[:i])
        assert df.shape[0] == i


def test_model_prune():
    cols = ['filename', 'display_image', 'tags']
    df1 = makeOneLineDf(cols[:2], ['a', 'b'])
    df2 = makeOneLineDf(cols, ['a', 'b', None])
    pruned = model.prune(df1)
    assert pruned['filename'].equals(df2['filename'])
    assert pruned['display_image'].equals(df2['display_image'])
    assert pruned['tags'].equals(df2['tags'])


def test_csv_tag_round_trip(tmp_path):
    first = TableItem(str(tmp_path / 'first.jpg'))
    first.setTags(['图片', '收藏', '图片'])
    second = TableItem(str(tmp_path / 'second.mp4'))
    second.setTags('视频, 26年1月')
    csv_path = tmp_path / 'records.csv'

    model.save([first, second], str(csv_path))
    loaded = model.load(str(csv_path))
    restored = TableItem.fromRecords(loaded)

    assert list(loaded.columns) == ['filename', 'display_image', 'tags']
    assert restored[0].tags == ['图片', '收藏']
    assert restored[1].tags == ['视频', '26年1月']
    assert not any(column.startswith('Unnamed:') for column in loaded.columns)


def test_empty_csv_round_trip_has_expected_columns(tmp_path):
    csv_path = tmp_path / 'empty.csv'
    model.save([], str(csv_path))

    loaded = model.load(str(csv_path))

    assert loaded.empty
    assert list(loaded.columns) == ['filename', 'display_image', 'tags']


def test_sidecar_metadata_round_trip_is_utf8_and_atomic(tmp_path):
    csv_path = tmp_path / 'records.csv'
    metadata = {
        'work_dir': str(tmp_path),
        'tag_schema_version': 1,
        'exclusive_groups': [
            {'id': 'file-type', 'name': '文件类型', 'tags': ['图片', '视频']},
        ],
        'coexist_tags': ['收藏'],
    }

    sidecar_path = model.saveMetadata(str(csv_path), metadata)
    loaded = model.loadMetadata(str(csv_path))

    assert sidecar_path == str(tmp_path / 'records.json')
    assert loaded == metadata
    assert json.loads((tmp_path / 'records.json').read_text(encoding='utf-8')) == metadata
    assert list(tmp_path.glob('*.tmp')) == []


def test_old_csv_and_sidecar_remain_compatible(tmp_path):
    csv_path = tmp_path / 'legacy.csv'
    pd.DataFrame([
        {'filename': 'legacy.jpg', 'display_image': None},
    ]).to_csv(csv_path)
    (tmp_path / 'legacy.json').write_text(
        json.dumps({'work_dir': str(tmp_path)}),
        encoding='utf-8',
    )

    loaded = model.load(str(csv_path))
    metadata = model.loadMetadata(str(csv_path))

    assert list(loaded.columns) == ['filename', 'display_image', 'tags']
    assert loaded.iloc[0]['tags'] is None
    assert metadata == {'work_dir': str(tmp_path)}


def test_invalid_sidecar_falls_back_to_empty_metadata(tmp_path):
    csv_path = tmp_path / 'broken.csv'
    (tmp_path / 'broken.json').write_text('{invalid', encoding='utf-8')

    assert model.loadMetadata(str(csv_path)) == {}


if __name__ == '__main__':
    pass
