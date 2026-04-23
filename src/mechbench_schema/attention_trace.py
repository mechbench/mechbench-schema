"""Attention-trace data shapes.

Records indexed by `(layer, head, position_from, position_to)` — the
attention patterns that heads compute during a forward pass. An
attention trace for a single prompt over a full model is a collection
of `(layer, head)` weight matrices, each `[seq_len × seq_len]` for
self-attention.

This module organizes the attention-pattern axis as a first-class
category, parallel to per_layer_data and per_head_data. A downstream
consumer can render a single (layer, head) matrix as a heatmap, a
small-multiples grid over (layer, head), a per-head attention-entropy
summary, etc.

The kinds today:

  attention_pattern — one (layer, head) attention matrix, possibly
                      bundled with token labels for axis rendering.
                      This is the atomic unit; a full trace is a
                      collection of these.

Future kinds (file when a real consumer needs them):
- attention_entropy — per-(layer, head, position) scalar summary.
- attention_topk    — per-(layer, head, position) top-k target
                      positions by weight.
- attention_trace   — a sweep containing many attention_patterns plus
                      shared metadata (prompt_id, token_labels). May
                      want a `PerHeadOf[AttentionPattern]`-style
                      container when task 000157's generic work lands.

Migrated from the old records.py as part of the domain-axis reorg
(task 000156).
"""

from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class AttentionPattern(BaseModel):
    """Post-softmax attention weights for one (layer, head) over a sequence.

    The weights matrix is stored as a flat row-major `[n_queries * n_keys]`
    list. Consumers reshape on ingest; this keeps the wire format
    JSON-native and trivially diffable. `token_labels`, when present,
    labels both axes (self-attention) — for cross-attention the caller
    should split into query_labels / key_labels (not yet modeled;
    add when needed).
    """

    kind: Literal["attention_pattern"] = "attention_pattern"
    layer: int = Field(..., ge=0, description="0-indexed transformer layer.")
    head: int = Field(..., ge=0, description="0-indexed attention head within the layer.")
    n_queries: int = Field(..., ge=1, description="Query-side sequence length.")
    n_keys: int = Field(..., ge=1, description="Key-side sequence length.")
    weights: list[float] = Field(
        ...,
        description=(
            "Row-major flattened post-softmax weights, shape "
            "[n_queries * n_keys]. weights[q * n_keys + k] is the attention "
            "weight from query q to key k."
        ),
    )
    token_labels: list[str] | None = Field(
        None,
        description=(
            "Optional per-position decoded tokens, for axis labelling. "
            "Assumes self-attention (same labels on both axes); if the "
            "shape is asymmetric, model the split explicitly."
        ),
    )


# --- Discriminated union over all attention-trace kinds ---------------------

AttentionTraceData = Annotated[
    Union[AttentionPattern],
    Field(discriminator="kind"),
]
