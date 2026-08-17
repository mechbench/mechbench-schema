"""Provenance and fidelity — the emission envelope (task 000237).

Every object emitted to the bench carries a `Provenance` record: when it
was created, what tool produced it, what prior objects it was computed
from, and a fingerprint of the run configuration. The `inputs` list is
the raw material for the lineage index (the API derives parent/child
edges from it at write time) and, later, for the 000162 memoization
cache keys — declared once here, consumed by both.

`Fidelity` is the governed recording-granularity choice for document
data (`docs/THE_BENCH.md` §4.1). The three levels form a degradation
chain:

    trace ⊃ segments ⊃ text

`trace` carries token ids, tokenizer identity, offset maps, and
generation spans; `segments` carries structure as strings (turns,
envelope regions) without token ids; `text` carries decoded strings
only. Downgrading is mechanical; upgrading is impossible without
re-running the model. Records declare the level they carry; consumers
(annotation layers, views, analyses) declare the level they require;
compare with `fidelity_satisfies` so mismatches fail at validation
time, not render time. When recording is cheap, record high — the
levels exist for when it is not.

Nothing in this module mandates an envelope shape for *payloads*; the
`Emitted` wrapper is the generic transport form (provenance + payload)
used by the emission spine for payloads that don't yet have a typed
home. Typed record families adopt provenance by carrying an optional
`Provenance` field directly (see `PerLayerBase.provenance`) — optional
on read for backward tolerance, required on new writes by the API.
"""

from __future__ import annotations

import hashlib
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from .codec_cbor import dump_canonical
from .identity import MechbenchPath


class ToolInfo(BaseModel):
    """The producing tool, pinned to a version.

    `tool` is a package or script identity (e.g. 'mechbench-core');
    `version` is its release or commit identifier. Together they are the
    coarse code-fingerprint until 000162 introduces fine-grained ones.
    """

    tool: str = Field(..., description="Producing package/script id, e.g. 'mechbench-core'.")
    version: str = Field(..., description="Version or commit of the producing tool.")


class Fidelity(str, Enum):
    """Recording granularity for document data. See module docstring for
    the degradation-chain contract."""

    TEXT = "text"
    SEGMENTS = "segments"
    TRACE = "trace"


_FIDELITY_ORDER: dict[Fidelity, int] = {
    Fidelity.TEXT: 0,
    Fidelity.SEGMENTS: 1,
    Fidelity.TRACE: 2,
}


def fidelity_satisfies(actual: Fidelity, required: Fidelity) -> bool:
    """True when a record at `actual` fidelity can serve a consumer
    requiring `required` (i.e. actual is at least as fine-grained)."""
    return _FIDELITY_ORDER[actual] >= _FIDELITY_ORDER[required]


def fingerprint_params(params: Any) -> str:
    """Canonical fingerprint of a run configuration: sha256 over the
    canonical-CBOR encoding, as 'sha256:<hex>'. Canonical encoding makes
    the fingerprint stable across languages and dict orderings."""
    digest = hashlib.sha256(dump_canonical(params)).hexdigest()
    return f"sha256:{digest}"


class Provenance(BaseModel):
    """What produced an emitted object, from what, when.

    `created_at` is an ISO-8601 UTC timestamp string (e.g.
    '2026-08-17T21:04:05Z'). `inputs` are the MechbenchPaths (including
    `~hash/...` forms) of the objects this one was computed from — the
    lineage index is derived from this list at emission time.
    `params_fingerprint` comes from `fingerprint_params` over the run
    config. `schema_version` records the mechbench-schema version the
    object was written under.
    """

    created_at: str = Field(..., description="ISO-8601 UTC timestamp, e.g. '2026-08-17T21:04:05Z'.")
    produced_by: ToolInfo
    inputs: list[MechbenchPath] = Field(
        default_factory=list,
        description="Paths of the objects this one was computed from.",
    )
    params_fingerprint: str | None = Field(
        None,
        description="'sha256:<hex>' fingerprint of the run configuration (fingerprint_params).",
    )
    schema_version: str = Field(..., description="mechbench-schema version at write time.")
    fidelity: Fidelity | None = Field(
        None,
        description="Recording granularity, for document-bearing objects; None otherwise.",
    )


class Emitted(BaseModel):
    """Generic transport envelope: provenance + an arbitrary payload.

    Used by the emission spine for payloads that don't yet have a typed
    record family. Typed families carry `Provenance` directly instead of
    nesting under this wrapper.
    """

    provenance: Provenance
    payload: Any = Field(..., description="The emitted value; shape governed by its kind, not this wrapper.")
