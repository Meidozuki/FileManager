import os, sys
import pytest
import numpy as np
import pandas as pd

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


def test_model_config():
    model = Model()
    d = model.config
    model.saveConfig()
    assert os.path.exists('config.json')

    model.loadConfig()
    assert d == model.config
