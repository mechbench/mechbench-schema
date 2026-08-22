"""Per-head data shapes.

Records that associate some measurement with each attention head, indexed
by `(layer, head)`. The archetypal shape is a `[n_layers × n_heads]` grid
of scalars — per-head DLA contributions, per-head OV-circuit rank-0
singular values, per-head attention entropy.

This module organizes by domain axis (records indexed by layer + head),
not by consumer. The grid can be rendered as a heatmap, a sorted
leaderboard, a bar chart by layer aggregating across heads, or anything
else a downstream caller wants.

Composition with per_layer_data:
  A record that carries a full per-head structure at each layer (e.g.
  "at each layer, the top-5 heads and their OV directions") is a
  *nested* shape — see task 000157 for the generic `PerLayerOf[T]`
  container that would capture it. The flat `(layer, head)` indexing in
  this module is the common case.

The kinds today:

  per_head_scalar_grid — the archetypal shape. A [n_layers × n_heads]
                          float grid; semantics (DLA contribution,
                          entropy, silhouette score, etc.) live in the
                          envelope's `metric_name` / `metric_units`
                          fields, not in the payload kind.

Add a new kind when a concrete experiment needs a shape that isn't well-
served by the grid (e.g. per-head categorical labels from a
head-detector, per-head top-k token lists from OV-circuit analysis).
"""

from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


# --- Common envelope ---------------------------------------------------------

class PerHeadBase(BaseModel):
    """Fields every per-head data file carries.

    `n_heads` is the query-side head count per attention block;
    `n_kv_heads` is the (smaller) KV-side count under grouped-query
    attention. Charts rendering per-head data typically iterate the full
    n_heads × n_layers grid; some downstream analyses care about the
    KV-grouping (e.g. KV-sharing-boundary effects) and need n_kv_heads.
    """

    protocol: str = Field(..., description="Stable id of the producing protocol, e.g. 'step_32_per_head_dla'.")
    description: str = Field(..., description="Human-readable summary.")
    model: str = Field(..., description="HuggingFace model id.")
    n_layers: int = Field(..., ge=1, description="Total decoder-block count.")
    n_heads: int = Field(..., ge=1, description="Query-side attention heads per block.")
    n_kv_heads: int = Field(..., ge=1, description="KV-side attention heads per block (GQA).")
    global_layers: list[int] = Field(
        ...,
        description=(
            "Layer indices to be visually highlighted. Same semantics as the "
            "per_layer_data.PerLayerBase field."
        ),
    )


# --- Kind: per_head_scalar_grid ----------------------------------------------

class PerHeadScalarGrid(PerHeadBase):
    """[n_layers × n_heads] grid of scalar values, one per head.

    Covers the common archetypes: per-head DLA contribution, OV-circuit
    rank-0 singular value, attention entropy, Q/K silhouette, etc. The
    `metric_name` and `metric_units` fields on the envelope describe what
    the numbers *mean*; consumers render accordingly.

    The `values` field is stored as a flat row-major `[n_layers * n_heads]`
    list of floats rather than a nested `list[list[float]]`. This keeps
    the wire format JSON-native and trivially diffable; consumers reshape
    on ingest.
    """

    kind: Literal["per_head_scalar_grid"] = "per_head_scalar_grid"
    metric_name: str = Field(..., description="What the scalars measure (e.g. 'DLA contribution').")
    metric_units: str = Field(
        ...,
        description="Units for display (e.g. 'logit points'). Empty string if unitless.",
    )
    values: list[float] = Field(
        ...,
        description=(
            "Row-major [n_layers * n_heads] flat list. values[layer * n_heads + head] "
            "is the scalar for (layer, head)."
        ),
    )


# --- Discriminated union over all per-head kinds -----------------------------

PerHeadData = Annotated[
    Union[PerHeadScalarGrid],
    Field(discriminator="kind"),
]
