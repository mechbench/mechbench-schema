"""Emission record types.

Each model here describes the shape of one kind of interpretability datum
that crosses repo boundaries. Keep these models narrow, composable, and
versioned — changes here ripple to every consumer.
"""

from __future__ import annotations

from typing import Literal

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


class FactVectorRecord(BaseModel):
    """A single fact-vector observation.

    A fact vector is a residual-stream vector captured at a specific
    (hook_point, prompt, position). It is the atomic unit of the geometry
    analyses in mechbench-core.
    """

    hook_point: str = Field(
        ...,
        description="The hook name where this vector was captured, e.g. 'blocks.23.resid_post'.",
    )
    prompt_id: str
    position: int = Field(..., ge=0)
    layer: int = Field(..., ge=0)
    # d_model-length float32 vector. Use a flat list for JSON; parquet/npz for bulk storage.
    values: list[float]
    label: str | None = Field(
        None,
        description="Optional categorical label, e.g. 'capital-city', 'past-tense'.",
    )
    kind: Literal["residual", "attn_out", "mlp_out", "gate_out", "other"] = "residual"
