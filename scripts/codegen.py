"""Generate TypeScript types from the Pydantic models in mechbench_schema.

The Pydantic models are the single source of truth. This script:

  1. Exports each model's JSON Schema via model.model_json_schema().
  2. Emits a single consolidated JSON Schema file (for tooling that wants it).
  3. Uses `datamodel-code-generator` to produce TypeScript interfaces.
  4. Writes the result to ts/src/generated.ts.

CI enforces "no drift" by running this script and failing if the generated
output differs from what's committed. That guarantees the Python and TS
halves of the schema agree by construction.

Dependencies: datamodel-code-generator (pip install datamodel-code-generator)
Alternative TS emitters (json-schema-to-typescript via npm) also work; pick
one and stick with it.

Run:
    python scripts/codegen.py

Usage in CI:
    python scripts/codegen.py
    git diff --exit-code ts/src/generated.ts
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PY_PKG = REPO / "src" / "mechbench_schema"
TS_OUT = REPO / "ts" / "src" / "generated.ts"
JSON_OUT = REPO / "ts" / "src" / "schema.json"


def collect_schema() -> dict:
    """Import the package and build one JSON Schema document with $defs for every model."""
    sys.path.insert(0, str(REPO / "src"))
    import mechbench_schema  # noqa: E402

    defs: dict[str, dict] = {}
    for name in mechbench_schema.__all__:
        model = getattr(mechbench_schema, name)
        # Pydantic inlines nested models in $defs automatically.
        sub = model.model_json_schema(ref_template="#/$defs/{model}")
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


def generate_ts() -> None:
    TS_OUT.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "datamodel-codegen",
        "--input", str(JSON_OUT),
        "--input-file-type", "jsonschema",
        "--output", str(TS_OUT),
        "--output-model-type", "typescript",
    ]
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        print("datamodel-codegen not found. Install with: pip install 'datamodel-code-generator[typescript]'", file=sys.stderr)
        sys.exit(1)
    print(f"wrote {TS_OUT.relative_to(REPO)}")


if __name__ == "__main__":
    doc = collect_schema()
    write_json(doc)
    generate_ts()
