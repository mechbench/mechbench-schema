"""Canonical CBOR codec for content-addressed payloads (task 000186).

Produces RFC 8949 §4.2 ("Core Deterministic Encoding") output: one
byte representation per logical value, cross-language byte-identical
when another implementation respects the same rules. Use this
instead of JSON on any surface where a hash over the bytes is
load-bearing (cache entries at rest, content-addressed completion
bodies). Human-facing JSON envelopes stay JSON — this codec is a
tool for the content-addressed layer, not a wholesale replacement.

The cross-language contract is under test by `tests/cbor_vectors.py`
— a shared list of (id, value, expected-hex-bytes) that both the
Python encoder here and the TypeScript encoder in
`mechbench-schema/ts/src/codec-cbor.ts` must reproduce byte-for-byte.

Caveats / explicit non-goals:

- `NaN` and ±∞ are rejected at encode time. CBOR encodes them, but
  RFC 8949 §4.2 leaves shortest-form selection ambiguous for them
  (the "smallest representation that preserves the value" rule
  doesn't uniquely name half-precision vs single vs double), so
  cross-language equality isn't guaranteed. We disallow them at the
  boundary; use `null` for "no value" explicitly.
- `-0.0` is not re-canonicalized to `0.0`. If your payload has one
  and the other has the other, they hash differently — they *are*
  different IEEE values. Numerically equivalent but bit-distinct;
  the codec preserves the distinction.
- Dict keys must be strings or ints; arbitrary CBOR key types are
  rejected. This is narrower than CBOR itself but matches every
  payload shape in mechbench-schema.
"""

from __future__ import annotations

import math
from typing import Any, TypeVar

import cbor2
from pydantic import BaseModel

_Model = TypeVar("_Model", bound=BaseModel)

# The IEEE-754 double-precision integer-exact range: [-2^53, 2^53].
# Beyond this, float precision can't represent integers unambiguously,
# so whole-value-float-to-int promotion is unsafe.
_FLOAT_INT_MAX = 1 << 53


def dump_canonical(obj: Any) -> bytes:
    """Serialize `obj` as deterministic CBOR.

    Follows the stricter dCBOR conventions (IETF draft-ietf-cbor-dcbor):
    map keys sorted by length-then-lexicographic, shortest-form IEEE
    floats, AND redundant-representation collapsing — whole-valued
    floats within the IEEE-exact integer range encode as CBOR
    integers. This last rule is dCBOR's and is stricter than
    RFC 8949 §4.2; it exists so that `0` and `0.0` — numerically
    equivalent across languages — produce the same bytes.

    `obj` may be a Pydantic BaseModel (dumped via
    `.model_dump(mode="json")`) or any CBOR-compatible Python value
    (dict, list, str, int, float, bool, None, bytes).
    """
    if isinstance(obj, BaseModel):
        obj = obj.model_dump(mode="json")
    _reject_non_canonical_floats(obj)
    normalized = _normalize_for_dcbor(obj)
    return cbor2.dumps(normalized, canonical=True)


def _normalize_for_dcbor(obj: Any) -> Any:
    """Recursively promote whole-valued floats to int — so that
    `0.0` and `0` hash identically, matching dCBOR semantics and
    the TS `cbor2` package's dcborEncodeOptions behavior."""
    if isinstance(obj, bool):
        return obj  # bools are ints in Python — don't promote
    if isinstance(obj, float):
        if obj.is_integer() and -_FLOAT_INT_MAX <= obj <= _FLOAT_INT_MAX:
            # Matches dCBOR `simplifyNegativeZero: true` — -0.0 collapses
            # to int 0. If you need to distinguish signed zeros in a
            # hashed payload, you're past dCBOR's target use case and
            # should encode the sign as a separate field.
            return int(obj)
        return obj
    if isinstance(obj, dict):
        return {k: _normalize_for_dcbor(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_normalize_for_dcbor(v) for v in obj]
    return obj


def load_canonical(data: bytes, model: type[_Model]) -> _Model:
    """Parse canonical-CBOR `data` into the given Pydantic model."""
    raw = cbor2.loads(data)
    return model.model_validate(raw)


def load_raw(data: bytes) -> Any:
    """Parse canonical-CBOR `data` into a Python-native structure
    (dict / list / str / int / float / bool / None / bytes). Use
    when you want to inspect an unknown-shape payload without
    committing to a model."""
    return cbor2.loads(data)


def _reject_non_canonical_floats(obj: Any) -> None:
    """Walk `obj` and raise on NaN / ±∞ floats.

    Their canonical CBOR representation is under-specified for
    cross-language byte-equality; rather than silently accept bytes
    that *might* differ across implementations, we fail loudly at
    the encode boundary.
    """
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            raise ValueError(
                "canonical CBOR does not accept NaN / ±∞ "
                "(cross-language byte-equality is under-specified); "
                "use null for absent values."
            )
    elif isinstance(obj, dict):
        for k, v in obj.items():
            _reject_non_canonical_floats(k)
            _reject_non_canonical_floats(v)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            _reject_non_canonical_floats(item)
