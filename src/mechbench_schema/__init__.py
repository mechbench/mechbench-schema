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

from .attention_trace import (
    AttentionPattern,
    AttentionTraceData,
)
from .cluster_data import (
    Cluster,
    ClusterSet,
)
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
from .per_layer_per_position_data import (
    LogitLensTrajectory,
    PerLayerPerPositionBase,
    PerLayerPerPositionData,
)
from .vector_data import (
    CapturedVector,
    CentroidVector,
    HookKind,
    ProbeVector,
    SteeringVector,
    Vector,
)

__version__ = "0.7.0"

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
    # Attention-trace data (records indexed by (layer, head, position, position))
    "AttentionPattern",
    "AttentionTraceData",
    # Vector data (atomic directions in residual-stream space)
    "CapturedVector",
    "SteeringVector",
    "ProbeVector",
    "CentroidVector",
    "HookKind",
    "Vector",
    # Cluster data (collections of vectors with aggregate stats)
    "Cluster",
    "ClusterSet",
    # Per-(layer, position) data (residual-stream-axis records)
    "PerLayerPerPositionBase",
    "LogitLensTrajectory",
    "PerLayerPerPositionData",
]
