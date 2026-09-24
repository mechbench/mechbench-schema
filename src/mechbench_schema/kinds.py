from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

KIND_ROOT = "~canonical/kinds/"

COLLECTION = "collection"


class Space(BaseModel):
    """Where a vector lives: model, layer (null for a whole-model point
    such as the embedding), hook point, head (null unless per-head) and
    width. Two vectors are comparable only when their spaces agree."""

    model: str | None = None
    layer: int | None = None
    point: str
    head: int | None = None
    d: int = Field(..., gt=0)


class Token(BaseModel):
    """A token: its vocabulary id and its text."""

    id: int | None = None
    text: str | None = None


class TokenMass(BaseModel):
    """A token with its probability and log-probability."""

    token: Token
    p: float | None = None
    logp: float | None = None


class Distribution(BaseModel):
    """A next-token distribution summary: entropy in bits, the most likely
    tokens, and `tracked`, the tokens the caller asked about under the
    names it gave."""

    model_config = ConfigDict(extra="allow")

    entropy_bits: float
    top: list[TokenMass] = Field(default_factory=list)
    tracked: dict[str, TokenMass] = Field(default_factory=dict)


class RendererBindingSpec(BaseModel):
    """How a kind is drawn: a renderer primitive and the payload fields
    that fill its slots."""

    primitive: str
    field_map: dict[str, str] = Field(default_factory=dict)


class Kind(BaseModel):
    """A kind's declaration: its fields as JSON-Schema properties, which
    are required, what it extends, the key that identifies an item of it
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
    """Many items of one kind: `items` are of `item_kind`, sorted by `key`;
    any other field is header recorded by the producing operation."""

    model_config = ConfigDict(extra="allow")

    kind: str = Field(COLLECTION, pattern="^collection$")
    item_kind: str = Field(..., description="The bare name of the kind every item is.")
    key: list[str] = Field(default_factory=list, description="The item fields that identify an item; the stored order.")
    items: list[Any]
