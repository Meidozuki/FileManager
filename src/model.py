import os
import json
import logging
import numpy as np
import pandas as pd
from typing import List

from .vbao_wrapper import vbao
from .common import setupOneFileCategory, joinFileCategories
from .table_item import TableItem


class Model(vbao.Model):
    """
    model用来与磁盘交互，此处实现为无状态的工具类
    """

    def __init__(self):
        super().__init__()

        self.file_filters = {
            'image': 'jpg,png',
            'csv': 'csv',
            'all': '*'
        }

        self.default_config = {
            'temp_dir': 'savedata',
            'version': 0.1
        }
        self.config = self.default_config

    def getCategory(self, name):
        """
        get categories from self.file_filters, need be converted to QFileDialog format
        """
        return (name, self.file_filters[name].split(','))

    @property
    def save_format(self):
        return joinFileCategories([
            setupOneFileCategory(*self.getCategory('csv')),
            setupOneFileCategory(*self.getCategory('all'))
        ])

    @property
    def temp_dir(self) -> str:
        path = self.config["temp_dir"]
        if not os.path.exists(path):
            logging.info(f"temp dir {path} not exist, will mkdir")
            os.mkdir(path)
        return path

    # configure
    def saveConfig(self):
        with open('config.json', 'w') as f:
            json.dump(self.config, f)

    def loadConfig(self, path='config.json'):
        if os.path.exists(path):
            with open('config.json', 'r') as f:
                ctx = f.readlines()
            logging.info("read config.json:\n", ctx)
            self.config.update(json.loads('\n'.join(ctx)))
            logging.info(f"loaded config at {path}")
        elif path == 'config.json':
            logging.info("cannot find config.json, use default config")
        else:
            logging.warning(f"cannot find config file at {path}")

    # stateless operations
    def save(self, data: List[TableItem], save_dir: str):
        if len(data) == 0:
            return None

        df = self.changeItemToDf(data)
        df.to_csv(save_dir)
        return df

    def load(self, save_dir: str):
        if not os.path.exists(save_dir):
            logging.warning(f"Save file not found at {save_dir}. If you run this program the first time, ignore this.")
            return pd.DataFrame()

        df = pd.read_csv(save_dir)
        return df

    def prune(self, df: pd.DataFrame, *, testing_keys=None):
        temp = TableItem('')
        keys = temp.recordMapping().keys()
        if testing_keys is not None:
            keys = testing_keys

        for k in keys:
            if k not in df:
                df[k] = None

        return df[keys]

    def changeItemToDf(self, data: List[TableItem]):
        if len(data) == 0:
            return pd.DataFrame()

        cols = data[0].recordMapping().keys()
        arr = np.stack([list(item.recordMapping().values()) for item in data])
        return pd.DataFrame(
            arr,
            columns=cols
        )
