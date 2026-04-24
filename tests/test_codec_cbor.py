"""Verify the Python canonical-CBOR codec matches the shared vectors.

These vectors are the cross-language contract; the TypeScript codec
must produce byte-identical output on the same logical inputs. See
`cbor_vectors.py` for the hand-constructed expected-hex values.
"""

from __future__ import annotations

import pytest

from mechbench_schema.codec_cbor import (
    dump_canonical,
    load_canonical,
    load_raw,
)

from cbor_vectors import VECTORS  # noqa: E402 — tests/ is on sys.path via pytest


@pytest.mark.parametrize(("vid", "value", "expected_hex"), VECTORS)
def test_vector_hex(vid: str, value: object, expected_hex: str) -> None:
    got = dump_canonical(value).hex()
    assert got == expected_hex, (
        f"vector {vid}: got {got!r}, expected {expected_hex!r}"
    )


@pytest.mark.parametrize(("vid", "value", "expected_hex"), VECTORS)
def test_roundtrip_native(vid: str, value: object, expected_hex: str) -> None:
    encoded = dump_canonical(value)
    roundtripped = load_raw(encoded)
    assert roundtripped == value, f"vector {vid}: roundtrip mismatch"


def test_rejects_nan() -> None:
    with pytest.raises(ValueError, match="NaN"):
        dump_canonical(float("nan"))


def test_rejects_inf() -> None:
    with pytest.raises(ValueError, match="NaN"):
        dump_canonical(float("inf"))
    with pytest.raises(ValueError, match="NaN"):
        dump_canonical(float("-inf"))


def test_pydantic_roundtrip() -> None:
    """Exercise the Pydantic path with a model that ships in the package."""
    from mechbench_schema import LayerAblationPayload

    # Smallest valid payload.
    payload = LayerAblationPayload(
        experiment="test",
        description="x",
        model="m",
        n_layers=1,
        global_layers=[],
        prompts=[],
        aggregates={"mean": [], "median": []},
    )
    encoded = dump_canonical(payload)
    restored = load_canonical(encoded, LayerAblationPayload)
    assert restored == payload
