from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, model_validator


class PerLayerPerPositionBase(BaseModel):
    """Fields every per-(layer, position) record carries."""

    protocol: str = Field(
        ...,
        description="Stable id of the producing protocol, e.g. 'step_01_logit_lens_batch'.",
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


class LogitLensTrajectory(PerLayerPerPositionBase):
    """A target token's rank and log-probability under the logit lens at
    each (layer, position)."""

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


PerLayerPerPositionData = Annotated[
    Union[LogitLensTrajectory],
    Field(discriminator="kind"),
]
