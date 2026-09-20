import logging
import os

from .model import BaseDataModel


class KeiFileDataModel(BaseDataModel):

    @property
    def safe_temp_dir(self) -> str:
        path = self.config["temp_dir"]
        if not os.path.exists(path):
            logging.info(f"temp dir {path} not exist, will mkdir")
            os.mkdir(path)
        return path