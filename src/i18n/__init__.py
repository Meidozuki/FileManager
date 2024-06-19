
import os
import copy
import numpy as np
import pandas as pd

locale_file_mapping = {
    'chinese': 'cn',
    'english': 'eng'
}

import locale

def init():
    global _LANG, _dict

    _LANG = 'chinese'
    _dict = {}

    language_code, encoding = locale.getlocale()
    if str.lower(language_code).find('chinese') != -1:
        _LANG = 'chinese'

init()







def LOCTEXT(key, default=None, namespace=None):
    if default is None:
        default = key

    if key not in _dict:
        _dict[key] = (default)
    print(id(_dict))
    return _dict[key]


def save(path):
    global _dict
    print('save:',_dict)
    print(id(_dict))
    name, ext = os.path.splitext(path)
    if not ext:
        ext = '.xlsx'
    path = name + ext

    df = pd.DataFrame(columns=['key', 'value'])
    df['key'] = _dict.keys()
    df['value'] = _dict.values()
    print(df)
    if ext == '.xlsx':
        if os.path.exists(path):
            os.remove(path)
        df.to_excel(path)