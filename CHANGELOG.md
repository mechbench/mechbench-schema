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

## Unreleased

### Changes that raise

_None._ Every `EndpointRef` that validated before validates the same way.

### Changes that alter results without raising

_None._

### Other

- **`EndpointProvider` gains `deepseek`.** mechbench-compute's provider
  registry has had a DeepSeek entry, but the schema literal did not
  list it, so a DeepSeek `EndpointRef` failed validation. The literal
  now matches the registry exactly: `anthropic`, `openai`, `xai`,
  `gemini`, `fireworks`, `deepseek`, `openai-compatible`, `mock`. The
  TypeScript `Provider` type and `schema.json` gain the same value.
  `tests/test_endpoint_provider.py` is new: it validates an
  `EndpointRef` for every listed provider.

## 0.16.1 — 2026-09-23

### Changes that raise

_None._

### Changes that alter results without raising

_None._ A path that validated before validates the same way.

### Other

- **A hash segment is recognised before the named-segment length limit.**
  `_validate_segment` checked the 63-character limit first, so every
  `sha256:<64 hex>` segment (71 characters) was refused and no sha256
  hash path, global or scoped, could be written. That is why an object
  whose lineage cites a held-back intermediate by hash could not be
  stored (compute task 000666). A hash segment now has its own limit,
  145 characters, room for sha512; a named segment keeps 63, and a `:`
  outside a hash segment is still refused. `tests/test_identity.py` is
  new: its four hash cases fail on 0.16.0.

## 0.16.0 — 2026-09-15

### Changes that raise

- _None._

### Changes that alter results without raising

- **`Space`, `Token`, `TokenMass` and `Distribution` are the value
  types of the typology's second phase.** A vector item carries a
  `Space` (`{model, layer, point, head, d}`, all five always present);
  a token is `{id, text}`; a next-token summary is a `Distribution`
  (`entropy_bits`, `top` ranked as `TokenMass`, `tracked` by name).
  `Embeddings` is marked superseded by a `Collection` of
  `activations/vector` and kept for objects written in its shape.
- The TypeScript bindings gain the same four types.

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
