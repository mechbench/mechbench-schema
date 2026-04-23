"""Vector data shapes.

A vector is a single direction in residual-stream space, with metadata
describing where it came from and what it means. Unlike the
per-*-data modules (which organize records along architectural axes),
this module describes an **atomic** shape — one vector, one record.

Four origins today, discriminated by the `origin` field:

  captured    — A vector read from a specific (hook_point, prompt_id,
                 position, layer) during a forward pass. The atomic
                 unit of the geometry analyses in mechbench-core.
                 Migrated from the old records.py `FactVectorRecord`.
  steering    — A learned or derived direction applied as an
                 intervention. Carries the derivation story.
  probe       — A linear-probe weight vector. Carries what the probe
                 predicts.
  centroid    — The centroid of a cluster of vectors. Carries the
                 cluster id and member count.

Companion module: `cluster_data.py` (task 000160) uses these vectors as
the atomic members of a cluster.

Bulk storage caveat: a single d_model-wide float32 vector is
~10 KB of JSON; collections get heavy fast. See task 000161 for the
binary-transport story. For now, inline `values` on the wire; revisit
when real consumers hit the size limit.
"""

from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, model_validator


class _VectorBase(BaseModel):
    """Fields shared by every vector variant."""

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


# Hook-point kinds known to mechbench-core._arch.LAYER_HOOK_POINTS.
# Kept in a Literal to generate a tight TypeScript union on the UI side.
HookKind = Literal[
    "resid_pre",
    "resid_post",
    "attn_out",
    "mlp_out",
    "gate_out",
    "other",
]


class CapturedVector(_VectorBase):
    """A vector read from a hook point during a forward pass.

    Replaces the old `FactVectorRecord` from records.py. Adds the `origin`
    discriminator and renames the old `kind` field to `hook_kind` to make
    room for `origin` at the top level without collision.
    """

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
    """A learned or derived direction intended for intervention.

    Carries a description of how it was derived — usually a short
    natural-language note ("centroid of capital-city fact vectors minus
    centroid of person-name fact vectors at L23.resid_post", or "SVD
    component 0 of W_V for (L23, H5)"). Downstream consumers that need
    to reproduce or compose steering vectors read the description.
    """

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


# --- Discriminated union over all vector origins ----------------------------

Vector = Annotated[
    Union[CapturedVector, SteeringVector, ProbeVector, CentroidVector],
    Field(discriminator="origin"),
]
