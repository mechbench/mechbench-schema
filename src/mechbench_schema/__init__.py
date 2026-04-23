"""mechbench-schema — typed emission contract for the mechbench family.

This package is the single source of truth for every interpretability-record
shape that crosses a repo boundary. Python consumers (mechbench-core,
mechbench-agent, mechbench-remote, mechbench-experiments) import types from
here; TypeScript consumers (mechbench-ui) import types from the parallel
mechbench-schema npm package, which is generated from these Pydantic models
via scripts/codegen.py.

Rule of thumb: if the shape is ever serialized to disk, sent over the wire,
or rendered by a non-Python consumer, it belongs here. If the shape is only
used as an in-memory container within a single repo, it does not.
"""

from .per_head_data import (
    PerHeadBase,
    PerHeadData,
    PerHeadScalarGrid,
)
from .per_layer_data import (
    AblationPrompt,
    ConvergencePayload,
    ConvergenceRow,
    DlaPrompt,
    DlaSweepPayload,
    LayerAblationPayload,
    LayerAggregates,
    PerLayerBase,
    PerLayerData,
)
from .records import (
    LensTrajectory,
    LensStep,
    AttentionPattern,
    FactVectorRecord,
)

__version__ = "0.3.0"

__all__ = [
    # Per-layer data (records indexed by transformer layer)
    "PerLayerBase",
    "LayerAggregates",
    "AblationPrompt",
    "LayerAblationPayload",
    "DlaPrompt",
    "DlaSweepPayload",
    "ConvergenceRow",
    "ConvergencePayload",
    "PerLayerData",
    # Per-head data (records indexed by (layer, head))
    "PerHeadBase",
    "PerHeadScalarGrid",
    "PerHeadData",
    # Emission records (cross-repo)
    "LensTrajectory",
    "LensStep",
    "AttentionPattern",
    "FactVectorRecord",
]
