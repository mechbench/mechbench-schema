// Cross-language canonical-CBOR vector test.
// Mirrors mechbench-schema/tests/test_codec_cbor.py — same logical
// inputs, same expected hex. If both pass, the byte-identity
// invariant the content-addressability story requires is enforced
// across the Python / TS boundary.
//
// Plain node test runner (`node --test`) rather than a bundler-
// dependent framework so the schema package stays dep-light.

import assert from "node:assert/strict";
import { test } from "node:test";
import { Buffer } from "node:buffer";
import { dumpCanonical, loadCanonical } from "../codec-cbor.ts";

/**
 * Vectors must match `mechbench-schema/tests/cbor_vectors.py`
 * byte-for-byte. The JS representation of each Python value:
 *   - Python int → JS number (safe-int range only).
 *   - Python float → JS number. Whole-valued floats land as
 *     integers in JS automatically; to force "float 0.0" vs
 *     "int 0" we'd need BigDecimal/BigInt games, but under
 *     dCBOR they encode the same way anyway.
 *   - Python None → null.
 *   - Python dict → object.
 */
const VECTORS = [
  ["int_0", 0, "00"],
  ["int_1", 1, "01"],
  ["int_23", 23, "17"],
  ["int_24", 24, "1818"],
  ["int_neg_1", -1, "20"],
  ["int_neg_24", -24, "37"],
  ["int_neg_25", -25, "3818"],
  ["int_256", 256, "190100"],
  ["int_1000000", 1000000, "1a000f4240"],

  ["float_0", 0.0, "00"],
  ["float_neg_zero", -0.0, "00"],
  ["float_1_5", 1.5, "f93e00"],
  ["float_42_0", 42.0, "182a"],
  ["float_100000", 100000.0, "1a000186a0"],
  ["float_1_1", 1.1, "fb3ff199999999999a"],

  ["bool_true", true, "f5"],
  ["bool_false", false, "f4"],
  ["null", null, "f6"],

  ["str_empty", "", "60"],
  ["str_a", "a", "6161"],
  ["str_IETF", "IETF", "6449455446"],

  ["arr_empty", [], "80"],
  ["arr_1_2_3", [1, 2, 3], "83010203"],

  ["map_empty", {}, "a0"],
  ["map_ab", { a: 1, b: 2 }, "a2616101616202"],
  ["map_ba_reordered", { b: 2, a: 1 }, "a2616101616202"],

  [
    "layer_ablation_mini",
    { experiment: "demo", n_layers: 3, damage: [0.0, -1.5, 0.25] },
    "a3" +
      "6664616d616765" +
      "8300f9be00f93400" +
      "686e5f6c6179657273" +
      "03" +
      "6a6578706572696d656e74" +
      "6464656d6f",
  ],
];

for (const [id, value, expectedHex] of VECTORS) {
  test(`vector ${id}`, () => {
    const got = Buffer.from(dumpCanonical(value)).toString("hex");
    assert.equal(got, expectedHex, `vector ${id}: got ${got}, expected ${expectedHex}`);
  });
}

test("rejects NaN", () => {
  assert.throws(() => dumpCanonical(Number.NaN), /NaN/);
});

test("rejects Infinity", () => {
  assert.throws(() => dumpCanonical(Number.POSITIVE_INFINITY), /NaN/);
  assert.throws(() => dumpCanonical(Number.NEGATIVE_INFINITY), /NaN/);
});

test("roundtrip map", () => {
  const encoded = dumpCanonical({ a: 1, b: [2, 3] });
  const decoded = loadCanonical(encoded);
  assert.deepEqual(decoded, { a: 1, b: [2, 3] });
});
