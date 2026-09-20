import os, sys
import pytest

np = pytest.importorskip("numpy")
pd = pytest.importorskip("pandas")
pytest.importorskip("PIL")
pytest.importorskip("PySide6")

sys.path.append(os.path.abspath('..'))

from src.common import *
from src.models import KeiFileDataModel


def test_QFileDialog_format_1():
    output = convert_to_qt_file_suffix_filter('Images', 'png xpm jpg'.split())
    assert output == "Images (*.png *.xpm *.jpg)"


def test_QFileDialog_format_all_file():
    output = convert_to_qt_file_suffix_filter('All', ['*'])
    assert output == "All (*.*)"


def test_QFileDialog_format_multi():
    ls = [
        convert_to_qt_file_suffix_filter('Images', 'png xpm jpg'.split()),
        convert_to_qt_file_suffix_filter("Text files", ['txt']),
        convert_to_qt_file_suffix_filter("XML files", ['xml']),
    ]
    output = join_qt_file_suffix_filters(ls)
    assert output == "Images (*.png *.xpm *.jpg);;Text files (*.txt);;XML files (*.xml)"


def test_model_config(tmp_path):
    model = KeiFileDataModel()
    expected = dict(model.config)
    config_path = tmp_path / 'config.json'
    model.saveConfig(str(config_path))
    assert config_path.exists()

    model.loadConfig(str(config_path))
    assert expected == model.config
