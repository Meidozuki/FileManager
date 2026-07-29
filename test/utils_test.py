import os, sys
import pytest

np = pytest.importorskip("numpy")
pd = pytest.importorskip("pandas")
pytest.importorskip("PIL")
pytest.importorskip("PySide6")

sys.path.append(os.path.abspath('..'))

from src.common import *
from src.model import Model


def test_QFileDialog_format_1():
    output = setupOneFileCategory('Images', 'png xpm jpg'.split())
    assert output == "Images (*.png *.xpm *.jpg)"


def test_QFileDialog_format_all_file():
    output = setupOneFileCategory('All', ['*'])
    assert output == "All (*.*)"


def test_QFileDialog_format_multi():
    ls = [
        setupOneFileCategory('Images', 'png xpm jpg'.split()),
        setupOneFileCategory("Text files", ['txt']),
        setupOneFileCategory("XML files", ['xml']),
    ]
    output = joinFileCategories(ls)
    assert output == "Images (*.png *.xpm *.jpg);;Text files (*.txt);;XML files (*.xml)"


def test_model_config(tmp_path):
    model = Model()
    expected = dict(model.config)
    config_path = tmp_path / 'config.json'
    model.saveConfig(str(config_path))
    assert config_path.exists()

    model.loadConfig(str(config_path))
    assert expected == model.config
