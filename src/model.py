
import os
import logging
import pandas as pd
from typing import List

from .vbao_wrapper import vbao
from .table_item import TableItem


class Model(vbao.Model):
    """
    model用来与磁盘交互，此处实现为无状态的工具类
    """
    def __init__(self):
        super().__init__()

    def save(self, data: List[TableItem], save_dir: str):
        if len(data) == 0:
            return None

        df = data[0].toRecord()
        for r in data[1:]:
            df = pd.concat([df, r.toRecord()], copy=False)
        df = df.reset_index()
        df.to_csv(save_dir)
        return df

    def load(self, save_dir: str):
        if not os.path.exists(save_dir):
            logging.warning(f"Save file not found at {save_dir}. If you run this program the first time, ignore this.")
            return pd.DataFrame()

        df = pd.read_csv(save_dir)
        return df