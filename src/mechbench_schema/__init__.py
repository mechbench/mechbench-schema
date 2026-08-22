"""mechbench-schema — typed emission contract for the mechbench family.

This package is the single source of truth for every interpretability-record
shape that crosses a repo boundary. Python consumers (mechbench-core,
mechbench-runner, mechbench-remote, mechbench-experiments) import types from
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
from .codec_cbor import (
    dump_canonical,
    load_canonical,
    load_raw,
)
from .identity import (
    InvalidPathError,
    MechbenchPath,
    ParsedPath,
    PathCategory,
    make_canonical_path,
    make_global_hash_path,
    make_platform_path,
    make_scoped_hash_path,
    make_user_path,
    parse_path,
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
from .document_data import (
    AnnotationAnchor,
    AnnotationLayer,
    AnnotationValue,
    BASE_KIND_ANNOTATED_TOKENS,
    BASE_KIND_CONVERSATION,
    BASE_KIND_TEXT,
    DocumentCollection,
    DocumentItem,
    DocumentPayload,
    GenerationSpan,
    KindManifest,
    RendererBinding,
    Segment,
    Segmentation,
    Trace,
    Turn,
)
from .metric_data import (
    MetricColumn,
    MetricTable,
)
from .provenance import (
    Emitted,
    Fidelity,
    Provenance,
    ToolInfo,
    fidelity_satisfies,
    fingerprint_params,
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

__version__ = "0.12.0"

__all__ = [
    # Document collections + annotations + kind manifests (task 000239)
    "DocumentCollection",
    "DocumentItem",
    "DocumentPayload",
    "Trace",
    "GenerationSpan",
    "Segmentation",
    "Segment",
    "Turn",
    "AnnotationLayer",
    "AnnotationValue",
    "AnnotationAnchor",
    "KindManifest",
    "RendererBinding",
    "BASE_KIND_TEXT",
    "BASE_KIND_CONVERSATION",
    "BASE_KIND_ANNOTATED_TOKENS",
    # Metric tables (task 000244)
    "MetricTable",
    "MetricColumn",
    # Provenance + fidelity (the emission envelope, task 000237)
    "Provenance",
    "ToolInfo",
    "Emitted",
    "Fidelity",
    "fidelity_satisfies",
    "fingerprint_params",
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
    # Identity / namespacing (see docs/IDENTITY_AND_NAMESPACING.md)
    "MechbenchPath",
    "ParsedPath",
    "PathCategory",
    "InvalidPathError",
    "parse_path",
    "make_user_path",
    "make_canonical_path",
    "make_platform_path",
    "make_global_hash_path",
    "make_scoped_hash_path",
]

# Names that should be emitted to TS via codegen. Subset of __all__ — excludes
# Python-side utilities (functions, exceptions, non-Pydantic dataclasses)
# that don't cross the wire.
__schema_all__ = [
    # Per-layer data
    "PerLayerBase",
    "LayerAggregates",
    "AblationPrompt",
    "LayerAblationPayload",
    "DlaPrompt",
    "DlaSweepPayload",
    "ConvergenceRow",
    "ConvergencePayload",
    "PerLayerData",
    # Per-head data
    "PerHeadBase",
    "PerHeadScalarGrid",
    "PerHeadData",
    # Attention-trace data
    "AttentionPattern",
    "AttentionTraceData",
    # Vector data
    "CapturedVector",
    "SteeringVector",
    "ProbeVector",
    "CentroidVector",
    "HookKind",
    "Vector",
    # Cluster data
    "Cluster",
    "ClusterSet",
    # Per-(layer, position) data
    "PerLayerPerPositionBase",
    "LogitLensTrajectory",
    "PerLayerPerPositionData",
    # Identity (only the validated-string type crosses the wire; parsers and
    # helpers are Python-side-only)
    "MechbenchPath",
    "PathCategory",
]
