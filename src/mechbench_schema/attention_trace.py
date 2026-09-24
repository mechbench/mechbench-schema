from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class AttentionPattern(BaseModel):
    """Post-softmax attention weights for one (layer, head), flattened
    row-major."""

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
            "Optional per-position decoded tokens, labelling both axes "
            "(self-attention)."
        ),
    )


AttentionTraceData = Annotated[
    Union[AttentionPattern],
    Field(discriminator="kind"),
]
