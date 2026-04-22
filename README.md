# mechbench-schema

The typed emission contract for the [mechbench](https://github.com/mechbench/mechbench) family.

**Pydantic models are the single source of truth.** TypeScript bindings are generated from them; both halves are published from this one repo to two package registries.

| Consumer | Registry | Package |
| --- | --- | --- |
| Python (core, agent, remote, experiments) | PyPI | `pip install mechbench-schema` |
| TypeScript (ui, skills) | npm | `npm install mechbench-schema` |

The two packages share a name and a version. CI regenerates the TS bindings and fails on drift, so the two halves cannot disagree.

## Repo layout

```
mechbench-schema/
├── src/mechbench_schema/      # Pydantic models — the source of truth
│   ├── __init__.py
│   └── records.py
├── ts/                         # published to npm as "mechbench-schema"
│   ├── package.json
│   ├── tsconfig.json
│   └── src/
│       ├── index.ts
│       ├── generated.ts        # codegen output — DO NOT EDIT
│       └── schema.json         # consolidated JSON Schema — codegen output
├── scripts/
│   └── codegen.py              # Pydantic -> JSON Schema -> TypeScript
├── pyproject.toml              # published to PyPI as "mechbench-schema"
└── README.md
```

## Editing the contract

1. Edit (or add a new module under) `src/mechbench_schema/records.py`.
2. Export the new type from `src/mechbench_schema/__init__.py`.
3. Run `python scripts/codegen.py`. This writes `ts/src/schema.json` and `ts/src/generated.ts`.
4. Commit everything in one PR — Python source, generated JSON Schema, generated TypeScript.

CI runs codegen and `git diff --exit-code ts/src/generated.ts`. A drifted PR cannot land.

## Install (Python)

```bash
pip install mechbench-schema
```

```python
from mechbench_schema import LensTrajectory, LensStep

t = LensTrajectory(
    prompt_id="eiffel",
    target_token=" Paris",
    steps=[LensStep(layer=23, position=14, rank=3, logprob=-2.1, top_token=" France")],
)
```

## Install (TypeScript)

```bash
npm install mechbench-schema
```

```ts
import type { LensTrajectory } from "mechbench-schema";

const t: LensTrajectory = {
    prompt_id: "eiffel",
    target_token: " Paris",
    steps: [{ layer: 23, position: 14, rank: 3, logprob: -2.1, top_token: " France" }],
    metadata: {},
};
```

## Why one repo, two publications

Schemas that live in two repos drift. The only invariant that matters — "Python and TS agree on the shape" — is enforced by keeping the source in one place and generating the target. Consumers never need the other language's toolchain to install; `pip` and `npm` each resolve to a clean single-language package.

See [the family overview](https://github.com/mechbench/mechbench) for the rationale behind this and other multi-repo decisions.

## Status

Early. A handful of seed record types (`LensTrajectory`, `AttentionPattern`, `FactVectorRecord`) are defined; the full emission surface grows as `mechbench-core` formalizes its output. Track open work in the meta repo's [`tasks/mechbench-schema/`](https://github.com/mechbench/mechbench/tree/main/tasks/mechbench-schema) directory.

## License

MIT.
