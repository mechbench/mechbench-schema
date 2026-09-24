from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field

from .provenance import Provenance


class PerLayerBase(BaseModel):
    """Fields every per-layer record carries."""

    protocol: str = Field(..., description="Stable id of the producing protocol, e.g. 'step_02_layer_ablation'.")
    description: str = Field(..., description="Human-readable summary; appears in chart footers.")
    model: str = Field(..., description="HuggingFace model id.")
    n_layers: int = Field(..., ge=1, description="Total decoder-block count.")
    global_layers: list[int] = Field(
        ...,
        description=(
            "Layer indices to be visually highlighted. For Gemma 4 these are "
            "the global-attention layers; other architectures may use this for "
            "fresh-KV / MoE-routing / whatever architectural non-uniformity. "
            "Pass an empty list if the architecture has no layers worth "
            "highlighting."
        ),
    )
    provenance: Provenance | None = Field(
        None,
        description=(
            "Emission provenance. Optional on read; the API requires it "
            "on new writes."
        ),
    )


class LayerAggregates(BaseModel):
    """Per-layer summary statistics across a prompt battery."""

    mean: list[float] = Field(..., description="Per-layer mean; length equals n_layers.")
    median: list[float] = Field(..., description="Per-layer median; length equals n_layers.")


class AblationPrompt(BaseModel):
    """One prompt's contribution to a per-layer ablation sweep."""

    text: str
    target: str = Field(..., description="The model's own top-1 prediction on this prompt.")
    top1_id: int = Field(..., ge=0)
    baseline_logprob: float
    damage: list[float] = Field(
        ...,
        description="Δ log p per ablated layer; length equals n_layers. More negative = more damaging.",
    )


class LayerAblationPayload(PerLayerBase):
    """Per-layer ablation damage across a prompt battery."""

    kind: Literal["layer_ablation"] = "layer_ablation"
    prompts: list[AblationPrompt]
    aggregates: LayerAggregates


class DlaPrompt(BaseModel):
    """One prompt's contribution to a DLA sweep (target vs. distractor)."""

    target: str
    distractor: str
    text: str
    target_token_id: int = Field(..., ge=0)
    distractor_token_id: int = Field(..., ge=0)
    category: str = Field(
        ...,
        description=(
            "Prompt-set category tag (e.g. 'landmark', 'capital'). Pass an "
            "empty string when the prompt set has no categorical metadata."
        ),
    )
    diffs: list[float] = Field(
        ...,
        description="(target − distractor) logit per layer; length equals n_layers.",
    )


class DlaSweepPayload(PerLayerBase):
    """Per-layer (target - distractor) direct logit attribution across a
    prompt battery."""

    kind: Literal["dla_sweep"] = "dla_sweep"
    prompts: list[DlaPrompt]
    aggregates: LayerAggregates


class ConvergenceRow(BaseModel):
    """One source experiment's contribution to a cross-experiment summary."""

    id: str = Field(..., description="Stable experiment id.")
    title: str = Field(..., description="Human-readable title shown as the row label.")
    finding: str = Field(..., description="The findings-doc id (e.g. '04', '33').")
    source: str = Field(..., description="The script or artifact this row summarizes.")
    question: str = Field(..., description="The natural-language question the experiment answered.")
    metric_name: str
    metric_units: str = ""
    peak_layer: int = Field(..., ge=0, description="The layer this experiment most strongly fingerprinted.")
    peak_value: float | None = Field(
        None,
        description="Optional numeric peak value (metric-specific).",
    )
    peak_description: str = Field(..., description="One-paragraph description of the peak.")
    second_layers: list[int] = Field(
        ...,
        description=(
            "Secondary layers worth marking on the chart; rendered as smaller "
            "markers. Pass an empty list if the experiment has a single peak."
        ),
    )


class ConvergencePayload(PerLayerBase):
    """Cross-experiment summary: N source experiments, one peak layer each."""

    kind: Literal["convergence"] = "convergence"
    pivot_layer: int = Field(..., ge=0, description="The layer the convergence centers on.")
    experiments: list[ConvergenceRow]


PerLayerData = Annotated[
    Union[LayerAblationPayload, DlaSweepPayload, ConvergencePayload],
    Field(discriminator="kind"),
]
