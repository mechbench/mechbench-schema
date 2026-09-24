from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from .provenance import Provenance


class MetricColumn(BaseModel):
    name: str
    dtype: Literal["number", "string"]
    description: str = ""


class MetricTable(BaseModel):
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
