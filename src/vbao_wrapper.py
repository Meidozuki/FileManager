import os
import sys


_module_dir = os.path.dirname(os.path.abspath(__file__))
_vbao_candidates = [
    os.path.abspath(os.path.join(_module_dir, "..", "..", "VBAO", "python")),
    os.path.abspath(os.path.join(_module_dir, "..", "VBAO", "python")),
]
for _candidate in _vbao_candidates:
    if os.path.isdir(_candidate) and _candidate not in sys.path:
        sys.path.insert(0, _candidate)
        break

import vbao