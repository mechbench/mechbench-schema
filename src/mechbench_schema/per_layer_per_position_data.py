"""Per-(layer, position) data shapes.

Records indexed along *both* the transformer-layer axis and the token-
position axis. The residual stream, and every observation derived from
it without compressing position away, lives here.

Per the task 000158 framing, future kinds include:

  logit_lens_trajectory — [n_layers × seq_len] ranks + logprobs of a
                           target token. Shipped today; migrates the
                           old LensStep/LensTrajectory from records.py.
  causal_trace_grid     — [n_layers × seq_len] post-intervention logit
                           differences (ROME-style plot). Add when a
                           real causal-tracing consumer arrives.
  per_position_attribution — [n_layers × seq_len] DLA values at each
                           position, for callers that want more than
                           the final-position scalar.
  residual_snapshot     — [n_layers × seq_len × d_model] vectors at
                           every (layer, position). Binary transport
                           needed before this can ship at scale; see
                           task 000161.

Serialization: per-(layer, position) tensors are stored as flat
row-major lists on the wire, length `n_layers * seq_len`. Consumers
reshape at ingest, same convention as attention_trace and
per_head_data.

The archetypal envelope carries sequence-level metadata (prompt_id,
prompt_text, token_labels) alongside the usual architectural metadata
(model, n_layers, seq_len, global_layers). Every kind in this module
inherits these fields.
"""

from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, model_validator


# --- Common envelope ---------------------------------------------------------

class PerLayerPerPositionBase(BaseModel):
    """Fields every per-(layer, position) record carries."""

    experiment: str = Field(
        ...,
        description="Stable script id, e.g. 'step_01_logit_lens_batch'.",
    )
    description: str = Field(..., description="Human-readable summary.")
    model: str = Field(..., description="HuggingFace model id.")
    n_layers: int = Field(..., ge=1, description="Total decoder-block count.")
    seq_len: int = Field(..., ge=1, description="Input sequence length.")
    global_layers: list[int] = Field(
        ...,
        description=(
            "Layer indices to be visually highlighted. Same semantics as the "
            "other domain-axis modules. Empty list if the architecture has "
            "no layers worth highlighting."
        ),
    )
    prompt_id: str = Field(
        ...,
        description="Identifier of the source prompt this record was computed against.",
    )
    prompt_text: str = Field(
        ...,
        description="The raw prompt text.",
    )
    token_labels: list[str] | None = Field(
        None,
        description=(
            "Optional per-position decoded tokens. Length equals seq_len "
            "when present. Useful for axis labelling. Absent when the "
            "positional labels aren't meaningful (e.g. for padding-heavy "
            "batched input)."
        ),
    )


# --- Kind: logit_lens_trajectory ---------------------------------------------

class LogitLensTrajectory(PerLayerPerPositionBase):
    """A logit-lens trajectory over layers and positions.

    Projects the residual stream at each (layer, position) through the
    model's output head and records the target token's rank and
    log-probability. Optionally records the argmax token at each
    position ("top_tokens"), useful for narrating a trajectory.

    The three flat lists (`ranks`, `logprobs`, optionally `top_tokens`)
    are all row-major `[n_layers * seq_len]`: index `layer * seq_len +
    position`. Consumers reshape at ingest.

    Replaces the old records.LensStep + records.LensTrajectory pair,
    which modeled one step per entry and paid struct-per-entry
    overhead. The flat-list shape is tighter on the wire and matches
    the convention used by the other per-layer and per-head modules.
    """

    kind: Literal["logit_lens_trajectory"] = "logit_lens_trajectory"
    target_token: str = Field(
        ...,
        description="The token whose rank and logprob are being tracked.",
    )
    target_token_id: int = Field(
        ...,
        ge=0,
        description="Tokenizer-specific id of target_token.",
    )
    ranks: list[int] = Field(
        ...,
        description=(
            "Rank of target_token under the lens at each (layer, position). "
            "Flat row-major, length n_layers * seq_len. 0 == top-1."
        ),
    )
    logprobs: list[float] = Field(
        ...,
        description=(
            "Log-probability of target_token under the lens at each "
            "(layer, position). Flat row-major, length n_layers * seq_len."
        ),
    )
    top_tokens: list[str] | None = Field(
        None,
        description=(
            "Optional per-(layer, position) argmax token under the lens. "
            "Flat row-major when present, length n_layers * seq_len. "
            "Useful for narrating layer-by-layer condensation of the "
            "model's prediction."
        ),
    )

    @model_validator(mode="after")
    def _flat_lengths_match(self) -> "LogitLensTrajectory":
        expected = self.n_layers * self.seq_len
        if len(self.ranks) != expected:
            raise ValueError(
                f"ranks length ({len(self.ranks)}) does not match "
                f"n_layers * seq_len ({expected})"
            )
        if len(self.logprobs) != expected:
            raise ValueError(
                f"logprobs length ({len(self.logprobs)}) does not match "
                f"n_layers * seq_len ({expected})"
            )
        if self.top_tokens is not None and len(self.top_tokens) != expected:
            raise ValueError(
                f"top_tokens length ({len(self.top_tokens)}) does not match "
                f"n_layers * seq_len ({expected})"
            )
        if self.token_labels is not None and len(self.token_labels) != self.seq_len:
            raise ValueError(
                f"token_labels length ({len(self.token_labels)}) does not match "
                f"seq_len ({self.seq_len})"
            )
        return self


# --- Discriminated union over all per-(layer, position) kinds ---------------

PerLayerPerPositionData = Annotated[
    Union[LogitLensTrajectory],
    Field(discriminator="kind"),
]
