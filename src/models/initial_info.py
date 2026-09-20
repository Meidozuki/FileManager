from enum import Enum
from typing import final, Final, Dict

@final
class FileVersion(Enum):
    V1 = 1

@final
class InitialInfo:
    def __init__(self):
        super().__init__()

        self.app_version: Final[str] = "0.2"
        self.file_version: Final[FileVersion] = FileVersion.V1

        self.file_filters: Dict[str, str] = {
            'image': 'jpg,png',
            'csv': 'csv',
            'all': '*'
        }
