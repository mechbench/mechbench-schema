# mechbench-schema

The typed emission contract for the [mechbench](https://github.com/mechbench/mechbench) family.

**Pydantic models are the single source of truth.** TypeScript bindings are generated from them; both halves are published from this one repo to two package registries.

| Consumer | Registry | Package |
| --- | --- | --- |
| Python (core, agent, remote, experiments) | PyPI | `pip install mechbench-schema` |
| TypeScript (ui, skills) | npm | `npm install mechbench-schema` |

The two packages share a name and a version. CI regenerates the TS bindings and fails on drift, so the two halves cannot disagree.

## Organization: by domain axis, not by consumer

Modules are named after the **indexing axis** of the records they carry, not after who renders them. This keeps the schema from becoming "chart data" just because charts are the current biggest consumer; the same records drive CSV exports, agent tool surfaces, the memoization cache, and anything else downstream.

| module | category | archetypal records |
|---|---|---|
| `per_layer_data` | indexed by `layer` | ablation damage, DLA diffs, convergence summaries |
| `per_head_data` | indexed by `(layer, head)` | per-head DLA, OV rank-0 singular values |
| `attention_trace` | indexed by `(layer, head, pos_from, pos_to)` | attention patterns |
| `per_layer_per_position_data` | indexed by `(layer, position)` | logit-lens trajectories, causal-trace grids |
| `vector_data` | atomic: one direction in residual space | captured / steering / probe / centroid vectors |
| `cluster_data` | collection of vectors with aggregate stats | named clusters, cross-cluster statistics |
| `identity` | path grammar | `MechbenchPath` validated-string type |

Every payload model is part of a discriminated union keyed by `kind` (or `origin` for vectors), so the UI can dispatch rendering on the tag and the DAG solver can reason about compatible outputs.

## Repo layout

```
mechbench-schema/
├── src/mechbench_schema/              # Pydantic models — the source of truth
│   ├── __init__.py                    # __all__ + __schema_all__
│   ├── attention_trace.py
│   ├── cluster_data.py
│   ├── identity.py
│   ├── per_head_data.py
│   ├── per_layer_data.py
│   ├── per_layer_per_position_data.py
│   └── vector_data.py
├── ts/                                # published to npm as "mechbench-schema"
│   ├── package.json
│   ├── tsconfig.json
│   └── src/
│       ├── index.ts
│       ├── generated.ts               # codegen output — DO NOT EDIT
│       └── schema.json                # consolidated JSON Schema — codegen output
├── scripts/
│   └── codegen.py                     # Pydantic → JSON Schema → TypeScript
├── pyproject.toml                     # published to PyPI as "mechbench-schema"
└── README.md
```

## Editing the contract

1. Edit an existing module under `src/mechbench_schema/`, or add a new module (following the domain-axis convention).
2. Export the new type from `src/mechbench_schema/__init__.py`. Add it to `__all__` for Python consumers and to `__schema_all__` for codegen (wire types only).
3. Run `python scripts/codegen.py`. This writes `ts/src/schema.json` and `ts/src/generated.ts`.
4. Commit everything in one PR — Python source, generated JSON Schema, generated TypeScript.

CI runs codegen and `git diff --exit-code ts/src/schema.json ts/src/generated.ts`. A drifted PR cannot land.

The codegen uses `json-schema-to-typescript` (via `npx`) for the TS emission. Python → JSON Schema comes from Pydantic's built-in `model_json_schema()` (for `BaseModel` subclasses) and `TypeAdapter(...).json_schema()` (for type aliases like the discriminated unions).

## Install (Python)

```bash
pip install mechbench-schema
```

```python
from mechbench_schema import LayerAblationPayload, DlaSweepPayload

payload = LayerAblationPayload(
    experiment="step_02_layer_ablation",
    description="Per-layer ablation damage on FACTUAL_15.",
    model="mlx-community/gemma-4-E4B-it-bf16",
    n_layers=42,
    global_layers=[5, 11, 17, 23, 29, 35, 41],
    prompts=[...],
    aggregates=LayerAggregates(mean=[...], median=[...]),
)

# Emit to JSON — mode="json" canonicalizes datetimes, bytes, etc.
import json
path.write_text(json.dumps(payload.model_dump(mode="json"), indent=2))
```

## Install (TypeScript)

```bash
npm install mechbench-schema
```

```ts
import type { LayerAblationPayload, Vector, MechbenchPath } from "mechbench-schema";

const payload: LayerAblationPayload = JSON.parse(text);
// All fields, discriminated unions, and nested types come from the generated bindings.
```

## Identity grammar

`MechbenchPath` is the type used to address every object in the mechbench family — charts, articles, experiments, corpuses, probes, cached DAG intermediates. Five categories:

- `<owner>/<project>/<folders>/<leaf>` — user-named
- `~canonical/<area>/<path>/<leaf>` — human-readable aliases for globally-shared content
- `~system/<area>/<path>/<leaf>` — platform / first-party
- `~hash/<algo>:<digest>` — global content-hashed (deduplicated across users)
- `<owner>/<project>/~hash/<algo>:<digest>` — workspace-scoped content-hashed

Full spec in the [meta repo's IDENTITY_AND_NAMESPACING.md](https://github.com/mechbench/mechbench/blob/main/docs/IDENTITY_AND_NAMESPACING.md). The Python side (`mechbench_schema.identity`) owns the authoritative validator; a mirror implementation lives in `mechbench-ui/src/lib/mechbenchPath.ts` for UI-side early failure.

## Why one repo, two publications

Schemas that live in two repos drift. The only invariant that matters — "Python and TS agree on the shape" — is enforced by keeping the source in one place and generating the target. Consumers never need the other language's toolchain to install; `pip` and `npm` each resolve to a clean single-language package.

See [the family overview](https://github.com/mechbench/mechbench) for the rationale behind this and other multi-repo decisions.

## Status

Version 0.8.0. Seven modules in active use; the legacy `records.py` holding pen was retired when the domain-axis reorg completed. `mechbench-experiments`' two exporters (`step_02_layer_ablation`, `step_33_dla_factual_sweep`) emit via Pydantic models; `mechbench-ui`'s chart interfaces are one-line aliases over the generated TS types.

Open work lives in the meta repo's [`tasks/mechbench-schema/`](https://github.com/mechbench/mechbench/tree/main/tasks/mechbench-schema) directory. The two notable open epics downstream of this repo:

- **[`000161`](https://github.com/mechbench/mechbench/tree/main/tasks/mechbench-schema/open)** — compact binary formats for records at rest and in transit (safetensors for tensor-bulk, parquet for record-collections).
- **[`000163`](https://github.com/mechbench/mechbench/tree/main/tasks/mechbench-meta/open)** — the identity-and-namespacing epic that produced `MechbenchPath`; Phase 4 (content-addressing grammar) remains open and coordinates with [`000162`](https://github.com/mechbench/mechbench/tree/main/tasks/mechbench-core/open) (the DAG-solver epic in `mechbench-core`).

## License

MIT.
