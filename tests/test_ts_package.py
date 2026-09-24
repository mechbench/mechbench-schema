from __future__ import annotations

import re
from pathlib import Path

TS_SRC = Path(__file__).resolve().parent.parent / "ts" / "src"


def test_relative_imports_carry_the_js_extension_node_esm_requires() -> None:
    bad = [
        f"{p.name}: {spec}"
        for p in TS_SRC.glob("*.ts")
        for spec in re.findall(r'from\s+"(\.{1,2}/[^"]+)"', p.read_text())
        if not spec.endswith(".js")
    ]
    assert not bad, bad
