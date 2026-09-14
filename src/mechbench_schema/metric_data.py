"""Metric tables — aggregate results referencing their inputs (task
000244; docs/THE_BENCH.md §7 Phase C).

The record family between documents and charts: an analysis over one
or more collections/overlays producing named values. `row_axis`
declares what a row is:

  corpus     one row per collection (corpus-level statistics)
  item       one row per document item (per-story aggregates — the
             feed for layer-valued sorting, task 000243)
  condition  one row per experimental condition — under the 000248
             template model, one row per *binding* of a sweep, which
             is what makes cross-condition tables aligned by
             construction.

Rows are plain dicts keyed by column name so GenericChart-style
consumers can treat them as record arrays without unwrapping.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from .provenance import Provenance


class MetricColumn(BaseModel):
    name: str
    dtype: Literal["number", "string"]
    description: str = ""


class MetricTable(BaseModel):
    """A presentation table. Its kind is `records/table`; `metric_table`
    is the retired spelling objects written before the typology carry."""

    kind: Literal["records/table", "metric_table"] = "records/table"
    name: str
    description: str = ""
    row_axis: Literal["corpus", "item", "condition"]
    columns: list[MetricColumn]
    rows: list[dict[str, float | int | str | None]]
    provenance: Provenance | None = None

    @model_validator(mode="after")
    def _rows_match_columns(self) -> "MetricTable":
        declared = {c.name for c in self.columns}
        for i, row in enumerate(self.rows):
            extra = set(row) - declared
            if extra:
                raise ValueError(
                    f"row {i} has undeclared columns: {sorted(extra)[:3]}")
        return self
