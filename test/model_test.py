import os, sys
import pytest
import numpy as np
import pandas as pd

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


if __name__ == '__main__':
    pass
