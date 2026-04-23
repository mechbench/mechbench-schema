"""Cluster data shapes.

A cluster is a named group of vectors with optional aggregate stats (a
centroid, a member count, cross-cluster relationships). This module
captures the collection-shape category: one level up from the atomic
`Vector` records in `vector_data.py`, one level below the
architectural-axis modules.

Two records:

  Cluster     — one named group. id, label, members (list of Vectors),
                 optional centroid, optional metadata.
  ClusterSet  — a collection of clusters with cross-cluster stats
                 (pairwise centroid cosines, aggregate silhouette,
                 metadata).

Bulk caveat: `Cluster.members` is inline on the wire. A cluster of
thousands of d_model-wide vectors is multi-megabyte JSON. See task
000161 for the binary-transport path; for now, inline — revisit when a
real consumer hits the size limit.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from .vector_data import CentroidVector, Vector


class Cluster(BaseModel):
    """A named group of vectors with optional aggregate stats.

    `members` is stored inline for simplicity. `centroid` is optional —
    computed on demand by callers that care; a Cluster with many members
    but no centroid is a valid, useful record (the geometry analyses
    often compute cluster membership without materializing a centroid).
    """

    id: str = Field(..., description="Stable cluster identifier.")
    label: str = Field(
        ...,
        description=(
            "Human-readable cluster label (e.g. 'capital-city fact vectors'). "
            "Use empty string if the cluster is unlabeled."
        ),
    )
    members: list[Vector] = Field(
        ...,
        description=(
            "The member vectors, inline on the wire. Length should equal "
            "n_members (validated). For large clusters see task 000161 "
            "(binary transport) before scaling up."
        ),
    )
    centroid: CentroidVector | None = Field(
        None,
        description=(
            "Optional computed centroid. When present, its cluster_id "
            "should match this cluster's id (validated) and its n_members "
            "should match this cluster's n_members."
        ),
    )
    n_members: int = Field(
        ...,
        ge=0,
        description=(
            "Explicit member count. Validated against len(members). "
            "Useful for header-only reads that don't want to materialize "
            "the full members list."
        ),
    )
    metadata: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _member_count_matches(self) -> "Cluster":
        if len(self.members) != self.n_members:
            raise ValueError(
                f"members length ({len(self.members)}) does not match "
                f"n_members ({self.n_members})"
            )
        if self.centroid is not None:
            if self.centroid.cluster_id != self.id:
                raise ValueError(
                    f"centroid.cluster_id ({self.centroid.cluster_id!r}) "
                    f"does not match cluster id ({self.id!r})"
                )
            if self.centroid.n_members != self.n_members:
                raise ValueError(
                    f"centroid.n_members ({self.centroid.n_members}) does "
                    f"not match cluster n_members ({self.n_members})"
                )
        return self


class ClusterSet(BaseModel):
    """A collection of clusters plus cross-cluster aggregate stats.

    The pairwise-cosine matrix is stored as a flat upper-triangle list
    (excluding the diagonal), length `n * (n - 1) / 2` for `n` clusters,
    indexed row-major: entry `[i, j]` with `i < j` sits at index
    `i * (n - 1) - (i * (i - 1)) // 2 + (j - i - 1)`. Callers that want
    a square matrix reshape on ingest.
    """

    id: str = Field(..., description="Stable identifier for this cluster-set.")
    label: str = Field("", description="Human-readable label for the set.")
    clusters: list[Cluster] = Field(..., description="The member clusters.")
    pairwise_cosine: list[float] | None = Field(
        None,
        description=(
            "Flat upper-triangle (excluding diagonal) of the centroid-cosine "
            "matrix. Length n*(n-1)/2 for n clusters. None if centroids "
            "are not present on all clusters."
        ),
    )
    silhouette: float | None = Field(
        None,
        description=(
            "Aggregate silhouette score across all member vectors. None "
            "if not computed."
        ),
    )
    metadata: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _pairwise_cosine_length(self) -> "ClusterSet":
        if self.pairwise_cosine is not None:
            n = len(self.clusters)
            expected = (n * (n - 1)) // 2
            if len(self.pairwise_cosine) != expected:
                raise ValueError(
                    f"pairwise_cosine length ({len(self.pairwise_cosine)}) "
                    f"does not match expected upper-triangle size "
                    f"{expected} for {n} clusters"
                )
        return self
