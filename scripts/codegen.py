from __future__ import annotations

import inspect
import json
import subprocess
import sys
from pathlib import Path

from pydantic import BaseModel, TypeAdapter

REPO = Path(__file__).resolve().parent.parent
PY_PKG = REPO / "src" / "mechbench_schema"
TS_OUT = REPO / "ts" / "src" / "generated.ts"
JSON_OUT = REPO / "ts" / "src" / "schema.json"


def collect_schema() -> dict:
    sys.path.insert(0, str(REPO / "src"))
    import mechbench_schema  # noqa: E402

    names = getattr(mechbench_schema, "__schema_all__", mechbench_schema.__all__)

    defs: dict[str, dict] = {}
    for name in names:
        obj = getattr(mechbench_schema, name)
        if inspect.isclass(obj) and issubclass(obj, BaseModel):
            sub = obj.model_json_schema(ref_template="#/$defs/{model}")
        else:
            sub = TypeAdapter(obj).json_schema(ref_template="#/$defs/{model}")
        for dname, dval in sub.pop("$defs", {}).items():
            defs.setdefault(dname, dval)
        defs[name] = sub

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "mechbench-schema",
        "$defs": defs,
    }


def write_json(doc: dict) -> None:
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(f"wrote {JSON_OUT.relative_to(REPO)}")


HEADER = (
    "// GENERATED FILE. Do not edit by hand.\n"
    "// Re-run `python scripts/codegen.py` after changing the Pydantic source.\n"
    "\n"
)


def generate_ts() -> None:
    TS_OUT.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "npx",
        "--yes",
        "json-schema-to-typescript@^15",
        str(JSON_OUT),
        "--no-additionalProperties",
        "--unreachableDefinitions",
        "--bannerComment",
        "",
    ]
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    except FileNotFoundError:
        print("npx not found. Install Node.js (https://nodejs.org).", file=sys.stderr)
        sys.exit(1)
    TS_OUT.write_text(HEADER + result.stdout)
    print(f"wrote {TS_OUT.relative_to(REPO)}")


if __name__ == "__main__":
    doc = collect_schema()
    write_json(doc)
    generate_ts()
