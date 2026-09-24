from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, model_validator


class _VectorBase(BaseModel):
    values: list[float] = Field(
        ...,
        description=(
            "The vector's components. Length equals `dim`. Dtype is float "
            "on the wire; callers preserving bf16 should convert at the "
            "transport boundary."
        ),
    )
    dim: int = Field(
        ...,
        ge=1,
        description=(
            "Explicit dimensionality, for validation and for headers that "
            "need the dimension without loading the full values array."
        ),
    )
    label: str | None = Field(
        None,
        description="Optional categorical label (e.g. 'capital-city', 'past-tense').",
    )
    metadata: dict[str, str] = Field(
        default_factory=dict,
        description="Freeform string-keyed metadata for caller-specific extensions.",
    )

    @model_validator(mode="after")
    def _values_length_matches_dim(self) -> "_VectorBase":
        if len(self.values) != self.dim:
            raise ValueError(
                f"values length ({len(self.values)}) does not match dim ({self.dim})"
            )
        return self


HookKind = Literal[
    "resid_pre",
    "resid_post",
    "attn_out",
    "mlp_out",
    "gate_out",
    "other",
]


class CapturedVector(_VectorBase):
    """A vector read from a hook point during a forward pass."""

    origin: Literal["captured"] = "captured"
    hook_point: str = Field(
        ...,
        description="Fully qualified hook name, e.g. 'blocks.23.resid_post'.",
    )
    prompt_id: str = Field(..., description="Identifier of the source prompt.")
    position: int = Field(..., ge=0, description="0-indexed token position.")
    layer: int = Field(..., ge=0, description="0-indexed transformer layer.")
    hook_kind: HookKind = Field(
        "resid_post",
        description=(
            "The hook-point class this capture came from. Distinguishes "
            "residual-stream vectors from branch-output vectors (attn_out, "
            "mlp_out, gate_out) captured at the same layer."
        ),
    )


class SteeringVector(_VectorBase):
    """A direction for intervention; `derivation` says how it was obtained."""

    origin: Literal["steering"] = "steering"
    derivation: str = Field(
        ...,
        description="Short description of how this direction was derived.",
    )
    target_concept: str | None = Field(
        None,
        description="Optional: the concept this steering vector is meant to push toward.",
    )


class ProbeVector(_VectorBase):
    """A linear-probe weight vector.

    Classifies residual-stream vectors by projecting onto this direction.
    `target_label` names what the probe predicts; `classifier_type`
    distinguishes linear regression, logistic regression, etc.
    """

    origin: Literal["probe"] = "probe"
    target_label: str = Field(..., description="What the probe predicts.")
    classifier_type: Literal["linear", "logistic", "other"] = Field(
        "linear",
        description="The classifier family the weight vector was fit for.",
    )


class CentroidVector(_VectorBase):
    """The centroid of a cluster of vectors.

    `cluster_id` is the stable id of the cluster this is the centroid of;
    `n_members` is the size of that cluster at centroid-computation time.
    Typically emitted alongside the Cluster record from cluster_data.py.
    """

    origin: Literal["centroid"] = "centroid"
    cluster_id: str = Field(..., description="Stable id of the source cluster.")
    n_members: int = Field(
        ...,
        ge=1,
        description="Number of member vectors averaged into this centroid.",
    )


Vector = Annotated[
    Union[CapturedVector, SteeringVector, ProbeVector, CentroidVector],
    Field(discriminator="origin"),
]
