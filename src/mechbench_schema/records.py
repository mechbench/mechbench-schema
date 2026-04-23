"""Legacy emission record types awaiting domain-axis homes.

This file is a holding pen. As the domain-axis convention matures (see
per_layer_data.py / per_head_data.py / attention_trace.py /
vector_data.py), records here migrate to their proper modules. Task
000156 tracks the ongoing reorg.

Remaining residents:

  LensStep / LensTrajectory — indexed by (layer, position); will migrate
                               to per_layer_per_position_data.py when
                               that module lands (task 000158).

Once the last record leaves, this file gets deleted.

Previously housed, now migrated:
  - AttentionPattern → attention_trace.py (task 000155)
  - FactVectorRecord → vector_data.CapturedVector (task 000159)
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class LensStep(BaseModel):
    """One (layer, position) entry of a logit-lens trajectory."""

    layer: int = Field(..., ge=0, description="0-indexed transformer layer.")
    position: int = Field(..., ge=0, description="0-indexed token position.")
    rank: int = Field(..., ge=0, description="Rank of the target token under the lens readout.")
    logprob: float = Field(..., description="Log-probability of the target token at this (layer, position).")
    top_token: str | None = Field(
        None,
        description="The model's argmax token under the lens at this (layer, position). Optional.",
    )


class LensTrajectory(BaseModel):
    """A logit-lens trajectory over layers and (optionally) positions."""

    prompt_id: str = Field(..., description="Identifier of the source prompt.")
    target_token: str = Field(..., description="The token whose rank/logprob is being tracked.")
    steps: list[LensStep]
    metadata: dict[str, str] = Field(default_factory=dict)
