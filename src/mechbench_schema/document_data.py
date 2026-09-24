from __future__ import annotations

from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field, model_validator

from .identity import MechbenchPath
from .provenance import Fidelity, Provenance


class GenerationSpan(BaseModel):
    token_start: int = Field(..., ge=0)
    token_end: int = Field(..., ge=0, description="Exclusive.")
    model: str | None = None
    adapter: str | None = Field(None, description="Adapter path or id, if fused.")
    temperature: float | None = None
    top_p: float | None = None
    top_k: int | None = None
    seed: int | None = None


class Trace(BaseModel):
    token_ids: list[int]
    tokenizer: str = Field(..., description="Tokenizer identity, e.g. the HF model id.")
    text: str = Field(..., description="Decoded text of the full stream.")
    offsets: list[tuple[int, int]] = Field(
        ..., description="Per-token [start, end) char spans into `text`.")
    generation_spans: list[GenerationSpan] = Field(default_factory=list)


class Segment(BaseModel):
    role: str = Field(..., description="e.g. 'system', 'user_turn', 'assistant_turn', 'envelope_prefix', 'body', 'media'.")
    token_start: int | None = Field(None, ge=0)
    token_end: int | None = Field(None, ge=0)
    char_start: int | None = Field(None, ge=0)
    char_end: int | None = Field(None, ge=0)
    asset: MechbenchPath | None = Field(None, description="Content-addressed asset for media segments.")


class Segmentation(BaseModel):
    schema_name: str = Field(..., description="Segmentation schema id, e.g. 'conversation', 'envelope'.")
    segments: list[Segment]


class Turn(BaseModel):
    role: str
    text: str


class DocumentItem(BaseModel):
    id: str
    kind: MechbenchPath = Field(..., description="Item-kind path, e.g. '~canonical/kinds/text'.")
    text: str | None = Field(None, description="The document text (body view).")
    turns: list[Turn] | None = None
    trace: Trace | None = None
    segmentations: list[Segmentation] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentCollection(BaseModel):
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


class AnnotationAnchor(BaseModel):
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


class RendererBinding(BaseModel):
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
    kind: Literal["kind_manifest"] = "kind_manifest"
    path: MechbenchPath = Field(..., description="The kind's identity, e.g. '~canonical/kinds/text'.")
    title: str
    version: str = Field(..., description="Manifest version; immutable once registered.")
    item_schema: dict[str, Any]
    renderer: RendererBinding
    collection_renderer: RendererBinding | None = Field(
        None,
        description=(
            "Optional collection-level view: renders the current page of "
            "items onto one canvas "
            "(e.g. series -> one line per item, item id as legend). Small "
            "collections with a collection renderer default to it."
        ),
    )
    supersedes: list[MechbenchPath] = Field(
        default_factory=list,
        description=(
            "Registered paths this kind replaces. A registered manifest is "
            "immutable, so a superseded kind is marked here, on its "
            "successor, never on itself."
        ),
    )
    provenance: Provenance | None = None


BASE_KIND_TEXT = "~canonical/kinds/text"
BASE_KIND_CONVERSATION = "~canonical/kinds/conversation"
BASE_KIND_ANNOTATED_TOKENS = "~canonical/kinds/annotated-tokens"

DocumentPayload = Annotated[
    Union[DocumentCollection, AnnotationLayer, KindManifest],
    Field(discriminator="kind"),
]
