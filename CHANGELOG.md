# mechbench-schema — changelog

Every release carries two lists, and an empty one says `_None._`
rather than being omitted: "there were none" and "nobody thought about
it" must not look the same.

```markdown
## <version> — <date>

### Changes that raise

### Changes that alter results without raising
```

The convention and the reasoning are in
[`mechbench/docs/RELEASE_NOTES.md`](https://github.com/mechbench/mechbench/blob/main/docs/RELEASE_NOTES.md).
The short version: a change that raises costs a reader ten minutes; a
change that alters results without raising can cost them a finding,
and it is invisible exactly when it matters.

The release gate blocks until the version being released has an entry
with both headings.

---

## 0.15.0 — 2026-09-14

### Changes that raise

- _None._ Every model that existed still parses what it parsed;
  `MetricTable`, `Transcript` and `Agent` now also accept the kind
  names the typology gave them (`records/table`, `text/transcript`,
  `text/agent`) and default to those.

### Changes that alter results without raising

- **`Kind` and `Collection` are the typology's wire contract.** A kind
  is declared once (in mechbench-compute's lexicon) and published as a
  `Kind`: name, path, fields, required, `extends`, `key`, header,
  renderer. Every plural result is a `Collection`: `kind:
  "collection"`, `item_kind`, `key`, `items` in key order, and whatever
  header the producing operation recorded. `DocumentCollection` and
  `AnnotationLayer` remain as the shapes objects carried before, which
  the bench keeps as stored.
- `KindManifest.supersedes` names the registered paths a kind replaces,
  since a registered manifest is immutable and a superseded kind can
  only be marked on its successor.
- The TypeScript bindings gain `Kind`, `Collection` and
  `RendererBindingSpec`.

## Unreleased

Versions before this file existed are **not classified**. The
convention was adopted on 2026-09-11 (task 000434) and applied
backwards only in `mechbench-compute`, where experiment 024's numbers
were live enough to audit honestly. Classifying schema's history from
memory would have been fabrication, so it was not done.
