# Comments

This repo has almost no comments, by rule. The code says what it does; a
comment that repeats it, explains it, or narrates its history goes stale and
misleads the next reader. What remains falls into three kinds.

1. **Directives.** `noqa`, `type: ignore`, pragmas, lint and TypeScript
   directives, shebangs, license headers.
2. **Published text.** A pydantic model's class docstring and its
   `Field(description=...)` strings are data: `scripts/codegen.py` writes them
   into `ts/src/schema.json` and `ts/src/generated.ts`, which API consumers
   read. So only a model that appears in `schema.json`'s `$defs` may have a
   class docstring. Published text says what the type is, in as few words as
   possible, with no history, roadmap or task references.
3. **Facts about the outside world, or rules that span files**, that a capable
   reader could not get from the code. Each one becomes a test where a test can
   hold it (the canonical-CBOR vectors, which the TypeScript suite must carry
   byte for byte, are the example). Only when no test can hold it does it stay
   as one short comment: `# external: <the outside thing> — <the fact>`.

Everything else is deleted: module and function docstrings, section banners,
explanations, rationale, history, versions, dates, task ids, roadmaps and
commented-out code. Task ids appear nowhere outside `CHANGELOG.md`.

`tests/test_comments.py` enforces this for Python and for the hand-written
TypeScript under `ts/src/` (`generated.ts` is excluded; its comments are the
published descriptions).
