from __future__ import annotations

import pytest

from mechbench_schema.codec_cbor import (
    dump_canonical,
    load_canonical,
    load_raw,
)

from cbor_vectors import VECTORS  # noqa: E402


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
    from mechbench_schema import LayerAblationPayload

    payload = LayerAblationPayload(
        protocol="test",
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


def test_whole_floats_collapse_to_int_only_within_the_ieee_exact_range() -> None:
    assert dump_canonical(float(2**53)) == dump_canonical(2**53)
    assert dump_canonical(float(-(2**53))) == dump_canonical(-(2**53))
    beyond = dump_canonical(float(2**54))
    assert beyond != dump_canonical(2**54)
    assert beyond[0] in (0xFA, 0xFB)


def test_booleans_are_not_promoted_to_integers() -> None:
    assert dump_canonical([True, 1]).hex() == "82f501"


def test_the_typescript_suite_checks_the_same_vectors() -> None:
    import re
    from pathlib import Path

    mjs = Path(__file__).resolve().parent.parent / "ts" / "src" / "__tests__" / "codec-cbor.test.mjs"
    text = re.sub(r'"\s*\+\s*"', "", mjs.read_text())
    ts_ids = [
        i for i in re.findall(r'^\s*\[?\s*"(\w+)",', text, re.MULTILINE)
        if not re.fullmatch(r"[0-9a-f]+", i)
    ]
    assert ts_ids == [vid for vid, _, _ in VECTORS]
    for vid, _, expected_hex in VECTORS:
        assert f'"{expected_hex}"' in text, f"vector {vid}: hex differs in the TypeScript suite"
