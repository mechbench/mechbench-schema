"""Per-layer data shapes.

Records that associate some measurement with each transformer layer.
Today the measurements are numeric scalars per layer (ablation damage,
DLA diffs, convergence peak values); the category naturally extends
to per-layer vectors, matrices, categorical labels, and other
per-layer quantities that future experiments will produce.

This module organizes the schema by *domain axis* (records indexed by
layer), not by consumer. The UI renders these as charts, but the same
records could drive a CSV export, an agent's tool surface, or any
other downstream renderer.

The three kinds today:

  layer_ablation   — step_02-style: per-layer damage (Δ log p) from
                      ablating each layer in turn across a prompt battery.
  dla_sweep        — step_33-style: per-layer (target - distractor) logit
                      difference across a prompt battery.
  convergence      — cross-experiment summary: one peak_layer per source
                      experiment, with rich metadata per row.

Add a new kind by (a) writing the payload model here, (b) adding its kind
literal to PerLayerData, (c) exporting it from __init__.py, (d) re-running
scripts/codegen.py.
"""

from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field

from .provenance import Provenance


# --- Common envelope fields ---------------------------------------------------

class PerLayerBase(BaseModel):
    """Fields every per-layer chart-data file carries.

    `experiment` is the stable id of the source script (matches the Python
    module name). `model` is the HuggingFace model id. `n_layers` and
    `global_layers` describe the model's layer structure so charts can
    adapt across model variants (E4B: 42, E2B: 30, ...).
    """

    experiment: str = Field(..., description="Stable script id, e.g. 'step_02_layer_ablation'.")
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
            "Emission provenance (task 000237). Optional on read for "
            "records written before 0.9.0; the API requires it on new "
            "writes."
        ),
    )


class LayerAggregates(BaseModel):
    """Per-layer summary statistics across a prompt battery."""

    mean: list[float] = Field(..., description="Per-layer mean; length equals n_layers.")
    median: list[float] = Field(..., description="Per-layer median; length equals n_layers.")


# --- Kind 1: layer_ablation ---------------------------------------------------

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
    """step_02-shape: per-layer ablation damage across a prompt battery."""

    kind: Literal["layer_ablation"] = "layer_ablation"
    prompts: list[AblationPrompt]
    aggregates: LayerAggregates


# --- Kind 2: dla_sweep --------------------------------------------------------

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
    """step_33-shape: per-layer (target - distractor) DLA across a prompt battery."""

    kind: Literal["dla_sweep"] = "dla_sweep"
    prompts: list[DlaPrompt]
    aggregates: LayerAggregates


# --- Kind 3: convergence ------------------------------------------------------

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


# --- Discriminated union over all per-layer kinds ----------------------------

PerLayerData = Annotated[
    Union[LayerAblationPayload, DlaSweepPayload, ConvergencePayload],
    Field(discriminator="kind"),
]
