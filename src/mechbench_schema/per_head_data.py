from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class PerHeadBase(BaseModel):
    """Fields every per-head record carries."""

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


class PerHeadScalarGrid(PerHeadBase):
    """One scalar per (layer, head); `metric_name` and `metric_units` say
    what it measures."""

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


PerHeadData = Annotated[
    Union[PerHeadScalarGrid],
    Field(discriminator="kind"),
]
