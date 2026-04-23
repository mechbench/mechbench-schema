"""Generate TypeScript types from the Pydantic models in mechbench_schema.

The Pydantic models are the single source of truth. This script:

  1. Exports each model's JSON Schema via model.model_json_schema().
  2. Emits a single consolidated JSON Schema file (ts/src/schema.json).
  3. Uses `json-schema-to-typescript` (run via npx) to produce TypeScript
     interfaces.
  4. Writes the result to ts/src/generated.ts.

CI enforces "no drift" by running this script and failing if the generated
output differs from what's committed. That guarantees the Python and TS
halves of the schema agree by construction.

Dependencies:
  - Python: `pip install -e '.[codegen]'` (Pydantic is enough; we no longer
    rely on datamodel-code-generator's TypeScript mode, which upstream
    removed).
  - Node: `npx json-schema-to-typescript` is invoked at codegen time; no
    persistent install required but npx will fetch on first run.

Run:
    python scripts/codegen.py

Usage in CI:
    python scripts/codegen.py
    git diff --exit-code ts/src/schema.json ts/src/generated.ts
"""

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
    """Import the package and build one JSON Schema document with $defs for every model.

    Iterates `__all__` and produces a JSON schema for each public name.
    BaseModel subclasses use their own `model_json_schema`; type aliases
    (discriminated unions, etc.) route through TypeAdapter so they still
    appear in the schema.
    """
    sys.path.insert(0, str(REPO / "src"))
    import mechbench_schema  # noqa: E402

    defs: dict[str, dict] = {}
    for name in mechbench_schema.__all__:
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
