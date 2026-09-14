"""Kinds and the one container (mechbench's typology; the lexicon in
mechbench-compute is the declaration, this is its wire contract).

A *kind* names the shape of one object: two-level and bare
(`records/table`, `activations/vector`, `text/document`), registered in
the catalog under `~canonical/kinds/<name>`. Kinds form a lattice
through `extends`; a kind that declares a `key` can be collected.

A *collection* is the one plural container. Its `item_kind` names what
the items are, its `key` is the fields that identify an item, and the
items are stored in key order, so the same items in any order are the
same bytes. Whatever else the producing operation recorded rides in
the header beside `items`; the kind's declaration documents those
fields. There is no `Set<T>` or `List<T>` distinction: order is a
property of the key, and a map is a collection keyed by a string.

Older objects on the bench carry the shapes that preceded this — a
`document_collection`, a `metric_table`, a `residual_vectors` with
`rows` — and the models for those remain below and in their modules,
because the bench does not rewrite what it stored. Readers resolve
those spellings through the lexicon's alias table.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

#: Where a kind is registered: `KIND_ROOT + name`.
KIND_ROOT = "~canonical/kinds/"

#: The one container's kind.
COLLECTION = "collection"


class RendererBindingSpec(BaseModel):
    """How a kind is drawn: a platform renderer primitive and the
    payload fields that fill its slots (`{"rows": "items"}`,
    `{"text": "text"}`)."""

    primitive: str
    field_map: dict[str, str] = Field(default_factory=dict)


class Kind(BaseModel):
    """A kind's declaration, as the lexicon publishes it: what the
    object is, its fields as JSON-Schema property entries, which are
    required, what it extends, the key that identifies an item of it
    in a collection, and the header fields a collection of it carries."""

    name: str = Field(..., description="Two-level bare name, `family/kind`.")
    path: str = Field(..., description="Registered path, `~canonical/kinds/<name>`.")
    family: str
    summary: str
    doc: str = ""
    fields: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="Field name → JSON-Schema property (`type`, `description`, …).")
    required: list[str] = Field(default_factory=list)
    extends: str | None = Field(None, description="The kind this one refines; its fields are inherited.")
    key: list[str] = Field(
        default_factory=list,
        description="The fields that identify an item in a collection; empty means the kind is not collected.")
    header: dict[str, str] = Field(
        default_factory=dict,
        description="Field name → what it means, for the fields a collection of this kind carries beside `items`.")
    renderer: RendererBindingSpec | None = None
    collection_renderer: RendererBindingSpec | None = None
    platform: bool = Field(False, description="Produced by the platform rather than by an operation.")


class Collection(BaseModel):
    """The one container. `items` are of `item_kind`, sorted by `key`;
    the header (anything else) is whatever the producing operation
    recorded, documented on the item kind's declaration."""

    model_config = ConfigDict(extra="allow")

    kind: str = Field(COLLECTION, pattern="^collection$")
    item_kind: str = Field(..., description="The bare name of the kind every item is.")
    key: list[str] = Field(default_factory=list, description="The item fields that identify an item; the stored order.")
    items: list[Any]
