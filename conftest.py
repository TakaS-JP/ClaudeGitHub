"""pytest が accounting パッケージをimportできるようにプロジェクトルートをsys.pathに追加.

テストツリーから上位パッケージを参照するために必要.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
