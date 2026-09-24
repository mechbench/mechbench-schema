from __future__ import annotations

import math
from typing import Any, TypeVar

import cbor2
from pydantic import BaseModel

_Model = TypeVar("_Model", bound=BaseModel)

_FLOAT_INT_MAX = 1 << 53


def dump_canonical(obj: Any) -> bytes:
    if isinstance(obj, BaseModel):
        obj = obj.model_dump(mode="json")
    _reject_non_canonical_floats(obj)
    normalized = _normalize_for_dcbor(obj)
    return cbor2.dumps(normalized, canonical=True)


def _normalize_for_dcbor(obj: Any) -> Any:
    if isinstance(obj, bool):
        return obj
    if isinstance(obj, float):
        if obj.is_integer() and -_FLOAT_INT_MAX <= obj <= _FLOAT_INT_MAX:
            return int(obj)
        return obj
    if isinstance(obj, dict):
        return {k: _normalize_for_dcbor(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_normalize_for_dcbor(v) for v in obj]
    return obj


def load_canonical(data: bytes, model: type[_Model]) -> _Model:
    raw = cbor2.loads(data)
    return model.model_validate(raw)


def load_raw(data: bytes) -> Any:
    return cbor2.loads(data)


def _reject_non_canonical_floats(obj: Any) -> None:
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
