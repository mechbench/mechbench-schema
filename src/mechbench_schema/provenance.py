from __future__ import annotations

import hashlib
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, SerializerFunctionWrapHandler, model_serializer

from .codec_cbor import dump_canonical
from .identity import MechbenchPath


class ToolInfo(BaseModel):
    """The producing tool and its version or commit."""

    tool: str = Field(..., description="Producing package/script id, e.g. 'mechbench-compute'.")
    version: str = Field(..., description="Version or commit of the producing tool.")


class Fidelity(str, Enum):
    """Recording granularity of document data, finest first: trace (token
    ids, tokenizer, offsets, generation spans), segments (structure as
    strings), text (decoded strings only)."""

    TEXT = "text"
    SEGMENTS = "segments"
    TRACE = "trace"


_FIDELITY_ORDER: dict[Fidelity, int] = {
    Fidelity.TEXT: 0,
    Fidelity.SEGMENTS: 1,
    Fidelity.TRACE: 2,
}


def fidelity_satisfies(actual: Fidelity, required: Fidelity) -> bool:
    return _FIDELITY_ORDER[actual] >= _FIDELITY_ORDER[required]


def fingerprint_params(params: Any) -> str:
    digest = hashlib.sha256(dump_canonical(params)).hexdigest()
    return f"sha256:{digest}"


class ExtensionPin(BaseModel):
    """The extension version whose operation produced an object: its address, its counter, and the digest of its extension object."""

    address: MechbenchPath = Field(..., title="ExtensionAddress", description="The extension's address, '<owner>/<project>/extensions/<name>'.")
    version: int = Field(..., ge=1, title="ExtensionVersion", description="The extension's version counter.")
    hash: str = Field(..., title="ExtensionHash", pattern=r"^sha256:[0-9a-f]{64}$", description="'sha256:<hex>' digest of the extension object.")


class Provenance(BaseModel):
    """What produced an emitted object, from which inputs, and when."""

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
    operation: MechbenchPath | None = Field(
        None,
        description=(
            "The operation that produced this object: a registered op "
            "path when one exists."
        ),
    )
    extension: ExtensionPin | None = Field(
        None,
        description=(
            "The extension version that provided `operation`, when an "
            "extension did; absent for a core operation."
        ),
    )
    params_ref: MechbenchPath | None = Field(
        None,
        description=(
            "Path of a stored params object (recoverable, unlike "
            "params_fingerprint which is only verifiable)."
        ),
    )

    @model_serializer(mode="wrap")
    def drop_absent_extension(self, handler: SerializerFunctionWrapHandler) -> dict[str, Any]:
        out = handler(self)
        if out.get("extension") is None:
            out.pop("extension", None)
        return out


class Emitted(BaseModel):
    provenance: Provenance
    payload: Any = Field(..., description="The emitted value; shape governed by its kind, not this wrapper.")
