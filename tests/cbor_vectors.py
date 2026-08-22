"""Shared canonical-CBOR test vectors — the cross-language contract.

Each entry is (id, python-value, expected-hex). The Python codec's
`dump_canonical(value).hex()` must match `expected_hex` exactly; the
TypeScript codec in `mechbench-schema/ts/src/codec-cbor.ts` must do
the same on the equivalent JS value.

If both produce the same hex on all vectors, the promise holds:

    same bytes ⇒ same hash ⇒ same logical value

The vectors are hand-constructed (not derived from one implementation
or the other) — they come straight from RFC 8949 §A and §4.2.3, with
a few mechbench-specific shapes added at the end.

Their inputs are FROZEN. A string inside a vector is test data paired
with hand-computed hex, not a reference to anything: the envelope below
names `mechbench-core` because that is what produced it, and renaming
the package does not change bytes that were already written.
"""

from __future__ import annotations

from typing import Any

# (id, value, expected-hex-bytes)
VECTORS: list[tuple[str, Any, str]] = [
    # --- integers: shortest-form encoding (RFC 8949 §4.2.1)
    ("int_0", 0, "00"),
    ("int_1", 1, "01"),
    ("int_23", 23, "17"),
    ("int_24", 24, "1818"),
    ("int_neg_1", -1, "20"),
    ("int_neg_24", -24, "37"),
    ("int_neg_25", -25, "3818"),
    ("int_256", 256, "190100"),
    ("int_1000000", 1_000_000, "1a000f4240"),
    # --- floats: shortest-form IEEE that roundtrips (RFC 8949 §4.2.2),
    # with dCBOR's extra rule: whole-valued floats in the IEEE-exact
    # integer range collapse to integer encoding. So 0.0 encodes as
    # `00`, not `f90000` — 0 and 0.0 hash identically.
    ("float_0", 0.0, "00"),
    # dCBOR collapses -0.0 to int 0 (simplifyNegativeZero). If you
    # need to distinguish the sign, encode it in a separate field.
    ("float_neg_zero", -0.0, "00"),
    # 1.5 is exactly representable as half-precision.
    ("float_1_5", 1.5, "f93e00"),
    # Whole-valued floats collapse to int (dCBOR).
    ("float_42_0", 42.0, "182a"),
    # 100000 as float → integer encoding under dCBOR.
    ("float_100000", 100000.0, "1a000186a0"),
    # 1.1 is not exactly representable in single-precision → must be double.
    ("float_1_1", 1.1, "fb3ff199999999999a"),
    # --- booleans / null
    ("bool_true", True, "f5"),
    ("bool_false", False, "f4"),
    ("null", None, "f6"),
    # --- short strings
    ("str_empty", "", "60"),
    ("str_a", "a", "6161"),
    ("str_IETF", "IETF", "6449455446"),
    # --- arrays
    ("arr_empty", [], "80"),
    ("arr_1_2_3", [1, 2, 3], "83010203"),
    # --- maps: sorted by bytewise encoding of key (RFC 8949 §4.2.3)
    ("map_empty", {}, "a0"),
    ("map_ab", {"a": 1, "b": 2}, "a2616101616202"),
    # keys inserted out of order in the Python dict literal must still be
    # sorted on the wire.
    ("map_ba_reordered", {"b": 2, "a": 1}, "a2616101616202"),
    # --- mechbench-shaped: a miniature LayerAblationPayload-ish thing
    (
        "layer_ablation_mini",
        {
            "experiment": "demo",
            "n_layers": 3,
            "damage": [0.0, -1.5, 0.25],
        },
        # Maps canonicalize under RFC 8949 §4.2.3: keys sort by the
        # bytewise encoding of their CBOR form, which is length-first,
        # then lexicographic. So for "damage" (6) < "n_layers" (8) <
        # "experiment" (10), the on-wire order is damage, n_layers,
        # experiment — NOT alphabetic.
        #
        #   a3                          -- map(3)
        #     66 6461 6d61 6765         -- "damage"
        #     83 00 f9be00 f93400       -- [0 (was 0.0 → dcbor int), -1.5, 0.25]
        #     68 6e5f 6c61 7965 7273    -- "n_layers"
        #     03                        -- 3
        #     6a 65787065 72696d656e74  -- "experiment"
        #     64 64656d 6f              -- "demo"
        "a3"
        "6664616d616765"  # "damage"
        "8300f9be00f93400"  # [0, -1.5, 0.25]
        "686e5f6c6179657273"  # "n_layers"
        "03"
        "6a6578706572696d656e74"  # "experiment"
        "6464656d6f",  # "demo"
    ),
    # --- provenance envelope (task 000237): map-key canonical ordering
    # over a realistic Provenance dump, incl. None -> null and enum -> str
    (
        "provenance_envelope",
        {
            "created_at": "2026-08-17T21:00:00Z",
            "fidelity": "trace",
            "inputs": ["benji/proj/corpora/stories"],
            "params_fingerprint": None,
            "produced_by": {"tool": "mechbench-core", "version": "0.7.0"},
            "schema_version": "0.9.0",
        },
        "a666696e7075747381781a62656e6a692f70726f6a2f636f72706f72612f73746f7269657368666964656c6974796574726163656a637265617465645f617474323032362d30382d31375432313a30303a30305a6b70726f64756365645f6279a264746f6f6c6e6d65636862656e63682d636f72656776657273696f6e65302e372e306e736368656d615f76657273696f6e65302e392e3072706172616d735f66696e6765727072696e74f6",
    ),
]
