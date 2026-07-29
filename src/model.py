import os
import json
import logging
import tempfile
import pandas as pd
from typing import List, Mapping

from .vbao_wrapper import vbao
from .common import changeFileExt, setupOneFileCategory, joinFileCategories
from .table_item import TableItem


class Model(vbao.core.Model):
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
            'auto_show_image_file': True,
            'version': 0.1
        }
        self.config = dict(self.default_config)

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
    def saveConfig(self, path='config.json'):
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(self.config, file, ensure_ascii=False, indent=2)

    def loadConfig(self, path='config.json'):
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as file:
                ctx = file.readlines()
            logging.info("read config at %s", path)
            self.config.update(json.loads('\n'.join(ctx)))
            logging.info(f"loaded config at {path}")
        elif path == 'config.json':
            logging.info("cannot find config.json, use default config")
        else:
            logging.warning(f"cannot find config file at {path}")

    # stateless operations
    @staticmethod
    def metadataPath(csv_path: str) -> str:
        return changeFileExt(csv_path, "json")

    @staticmethod
    def _atomicWriteText(path: str, writer):
        target = os.path.abspath(path)
        directory = os.path.dirname(target) or os.getcwd()
        prefix = f".{os.path.basename(target)}."
        fd, temp_path = tempfile.mkstemp(prefix=prefix, suffix=".tmp", dir=directory)
        os.close(fd)
        try:
            writer(temp_path)
            os.replace(temp_path, target)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def save(self, data: List[TableItem], save_dir: str):
        df = self.changeItemToDf(data)
        if len(data) == 0:
            df = pd.DataFrame(columns=list(TableItem("").recordMapping().keys()))
        self._atomicWriteText(
            save_dir,
            lambda temp_path: df.to_csv(temp_path, index=False, encoding="utf-8"),
        )
        return df

    def saveMetadata(self, csv_path: str, metadata: Mapping):
        sidecar_path = self.metadataPath(csv_path)
        if os.path.abspath(sidecar_path) == os.path.abspath("config.json"):
            raise ValueError("metadata sidecar would overwrite application config.json")

        def write_json(temp_path):
            with open(temp_path, "w", encoding="utf-8") as file:
                json.dump(metadata, file, ensure_ascii=False, indent=2)
                file.flush()
                os.fsync(file.fileno())

        self._atomicWriteText(sidecar_path, write_json)
        return sidecar_path

    def loadMetadata(self, csv_path: str) -> dict:
        sidecar_path = self.metadataPath(csv_path)
        if not os.path.exists(sidecar_path):
            return {}
        try:
            with open(sidecar_path, "r", encoding="utf-8") as file:
                metadata = json.load(file)
            if not isinstance(metadata, dict):
                logging.warning("Ignoring non-object metadata at %s", sidecar_path)
                return {}
            return metadata
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            logging.warning("Cannot load metadata at %s: %s", sidecar_path, exc)
            return {}

    def load(self, save_dir: str):
        def fillNanAsNone(df):
            for col in df.columns:
                df[col] = df[col].apply(lambda x: x if not pd.isna(x) else None)
            return df

        if not os.path.exists(save_dir):
            logging.warning(f"Save file not found at {save_dir}. If you run this program the first time, ignore this.")
            return self.prune(pd.DataFrame())

        try:
            df = pd.read_csv(save_dir, encoding="utf-8")
        except pd.errors.EmptyDataError:
            df = pd.DataFrame()
        return self.prune(fillNanAsNone(df))

    def prune(self, df: pd.DataFrame, *, testing_keys=None):
        temp = TableItem('')
        keys = list(temp.recordMapping().keys())
        if testing_keys is not None:
            keys = list(testing_keys)

        for key in keys:
            if key not in df:
                df[key] = None

        return df[keys]

    def changeItemToDf(self, data: List[TableItem]):
        if len(data) == 0:
            return pd.DataFrame()

        columns = list(data[0].recordMapping().keys())
        records = [item.recordMapping() for item in data]
        return pd.DataFrame(records, columns=columns)
