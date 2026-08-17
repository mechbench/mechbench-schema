"""Document collections — the bench's central object (task 000239;
docs/THE_BENCH.md §4).

"Document" is a viewing contract, not a data shape. The layer
boundaries:

- `DocumentCollection` is the Layer-0 container: ordered items, a kind
  tag, a fidelity declaration, provenance. Pagination and storage
  depend on nothing else.
- Items carry substrate structures per their fidelity level:
  `text`-level items are strings; `segments`-level items add structure
  as strings (turns); `trace`-level items add the token stream — ids,
  tokenizer, offset map, and `GenerationSpan`s (sampling parameters on
  the spans that were sampled, absent on spans that were not).
- `Segmentation`s are interpretations over the stream, plural:
  conversation is one schema, an answer envelope is another, and both
  may coexist. A `media` segment references a content-addressed asset.
- `AnnotationLayer`s are overlay objects: they reference a collection,
  declare a required fidelity, and anchor typed values to items via
  token spans (trace-level) or segment/char spans (any level).
- `KindManifest` registers an item kind at a MechbenchPath: a JSON
  Schema for the payload plus a declarative renderer binding. Base
  kinds are themselves registered at `~canonical/kinds/...`.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field, model_validator

from .identity import MechbenchPath
from .provenance import Fidelity, Provenance


# --- trace substrate ---------------------------------------------------------

class GenerationSpan(BaseModel):
    """Sampling metadata for a span of tokens that was model-generated.
    Spans not covered by any GenerationSpan were input (user-typed,
    template, teacher-forced) — their lack of sampling metadata is
    itself structure."""

    token_start: int = Field(..., ge=0)
    token_end: int = Field(..., ge=0, description="Exclusive.")
    model: str | None = None
    adapter: str | None = Field(None, description="Adapter path or id, if fused.")
    temperature: float | None = None
    top_p: float | None = None
    top_k: int | None = None
    seed: int | None = None


class Trace(BaseModel):
    """The token stream an item was produced/processed as — the ground
    truth at `trace` fidelity. `offsets[i]` is the [start, end) char
    span of token i in `text`."""

    token_ids: list[int]
    tokenizer: str = Field(..., description="Tokenizer identity, e.g. the HF model id.")
    text: str = Field(..., description="Decoded text of the full stream.")
    offsets: list[tuple[int, int]] = Field(
        ..., description="Per-token [start, end) char spans into `text`.")
    generation_spans: list[GenerationSpan] = Field(default_factory=list)


class Segment(BaseModel):
    """One span-to-role mapping. Token indices at trace fidelity; char
    offsets (into the item's text) otherwise. `media` segments carry an
    asset reference instead of/alongside text spans."""

    role: str = Field(..., description="e.g. 'system', 'user_turn', 'assistant_turn', 'envelope_prefix', 'body', 'media'.")
    token_start: int | None = Field(None, ge=0)
    token_end: int | None = Field(None, ge=0)
    char_start: int | None = Field(None, ge=0)
    char_end: int | None = Field(None, ge=0)
    asset: MechbenchPath | None = Field(None, description="Content-addressed asset for media segments.")


class Segmentation(BaseModel):
    """A named interpretation of an item's stream. Multiple may coexist
    (e.g. 'conversation' and 'envelope' over the same trace)."""

    schema_name: str = Field(..., description="Segmentation schema id, e.g. 'conversation', 'envelope'.")
    segments: list[Segment]


class Turn(BaseModel):
    """Segments-fidelity conversation structure: role + text, no ids."""

    role: str
    text: str


class DocumentItem(BaseModel):
    """One item of a collection. Which fields are populated follows the
    collection's fidelity: `text` always; `turns` for segments-level
    conversations; `trace` + `segmentations` at trace level. `kind` is
    the item-kind path (a registered KindManifest or a base kind under
    ~canonical/kinds/...)."""

    id: str
    kind: MechbenchPath = Field(..., description="Item-kind path, e.g. '~canonical/kinds/text'.")
    text: str | None = Field(None, description="The document text (body view).")
    turns: list[Turn] | None = None
    trace: Trace | None = None
    segmentations: list[Segmentation] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentCollection(BaseModel):
    """Layer-0 container. The `items` key is what the API's /~items
    pagination slices; nothing else in the platform depends on item
    internals."""

    kind: Literal["document_collection"] = "document_collection"
    name: str
    description: str = ""
    fidelity: Fidelity
    item_kind: MechbenchPath = Field(..., description="Kind path shared by items (per-item kind may override).")
    items: list[DocumentItem]
    provenance: Provenance | None = None

    @model_validator(mode="after")
    def _items_match_fidelity(self) -> "DocumentCollection":
        if self.fidelity == Fidelity.TRACE:
            missing = [it.id for it in self.items if it.trace is None]
            if missing:
                raise ValueError(
                    f"fidelity=trace but items lack traces: {missing[:5]}")
        return self


# --- annotation overlays -----------------------------------------------------

class AnnotationAnchor(BaseModel):
    """Where a value attaches. Exactly one addressing mode:
    token span (requires trace fidelity), char span (any fidelity,
    optionally scoped to a segmentation's segment), whole segment
    (segment_index without char span), or whole item (neither)."""

    item_id: str
    token_start: int | None = Field(None, ge=0)
    token_end: int | None = Field(None, ge=0)
    segmentation: str | None = Field(None, description="Segmentation schema_name the segment_index refers to.")
    segment_index: int | None = Field(None, ge=0)
    char_start: int | None = Field(None, ge=0)
    char_end: int | None = Field(None, ge=0)

    @model_validator(mode="after")
    def _one_mode(self) -> "AnnotationAnchor":
        token = self.token_start is not None and self.token_end is not None
        chars = self.char_start is not None and self.char_end is not None
        if token and chars:
            raise ValueError("anchor cannot use both token and char spans")
        return self


class AnnotationValue(BaseModel):
    anchor: AnnotationAnchor
    value: float | str


class AnnotationLayer(BaseModel):
    """A typed overlay over one collection. Numeric layers drive
    coloring; string layers drive tooltips/labels."""

    kind: Literal["annotation_layer"] = "annotation_layer"
    name: str
    description: str = ""
    collection: MechbenchPath
    value_type: Literal["numeric", "string"]
    required_fidelity: Fidelity = Field(
        Fidelity.TEXT,
        description="Minimum collection fidelity this layer's anchors need (token-span layers: trace).")
    values: list[AnnotationValue]
    provenance: Provenance | None = None

    @model_validator(mode="after")
    def _anchors_within_declared_fidelity(self) -> "AnnotationLayer":
        uses_tokens = any(v.anchor.token_start is not None for v in self.values)
        if uses_tokens and self.required_fidelity != Fidelity.TRACE:
            raise ValueError(
                "layer uses token-span anchors; required_fidelity must be 'trace'")
        return self


# --- kind manifests ----------------------------------------------------------

class RendererBinding(BaseModel):
    """Declarative mapping of an item kind onto a platform renderer
    primitive. `field_map` maps primitive slots (e.g. 'text', 'tokens',
    'color_layer') to payload field names or annotation-layer names."""

    primitive: Literal["text", "token_highlighter", "chat", "table", "series"]
    field_map: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Primitive-slot -> payload-field mapping. series slots: rows "
            "(record-array field), x, y, label; optional orientation "
            "('horizontal' = domain left-to-right, default; 'vertical' = "
            "domain top-to-bottom)."
        ),
    )


class KindManifest(BaseModel):
    """Registration record for an item kind (Layer 2). `item_schema` is
    a JSON Schema for item payloads; string fields bearing annotatable
    text are marked with `x-mechbench-text: true`."""

    kind: Literal["kind_manifest"] = "kind_manifest"
    path: MechbenchPath = Field(..., description="The kind's identity, e.g. '~canonical/kinds/text'.")
    title: str
    version: str = Field(..., description="Manifest version; immutable once registered.")
    item_schema: dict[str, Any]
    renderer: RendererBinding
    collection_renderer: RendererBinding | None = Field(
        None,
        description=(
            "Optional collection-level view (docs/THE_BENCH.md §4.6 / task "
            "000250): renders the current page of items onto ONE canvas "
            "(e.g. series -> one line per item, item id as legend). Small "
            "collections with a collection renderer default to it."
        ),
    )
    provenance: Provenance | None = None


# Base kinds live here so both halves of the platform agree on them.
BASE_KIND_TEXT = "~canonical/kinds/text"
BASE_KIND_CONVERSATION = "~canonical/kinds/conversation"
BASE_KIND_ANNOTATED_TOKENS = "~canonical/kinds/annotated-tokens"

DocumentPayload = Annotated[
    Union[DocumentCollection, AnnotationLayer, KindManifest],
    Field(discriminator="kind"),
]
