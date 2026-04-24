/**
 * Canonical-CBOR codec — the cross-language byte-identical counterpart
 * to `mechbench_schema.codec_cbor` on the Python side. Task 000186.
 *
 * Follows the stricter dCBOR conventions (IETF draft-ietf-cbor-dcbor):
 * map keys sorted by length-then-lexicographic, shortest-form IEEE
 * floats, AND redundant-representation collapsing — whole-valued
 * floats within the IEEE-exact integer range encode as CBOR
 * integers, so `0` and `0.0` hash identically.
 *
 * Use this instead of JSON on any surface where a hash over the
 * bytes is load-bearing (cache entries at rest, content-addressed
 * completion bodies). Human-facing JSON envelopes stay JSON.
 */

import { encode, dcborEncodeOptions, decode } from "cbor2";

export function dumpCanonical(value: unknown): Uint8Array {
  rejectNonCanonicalFloats(value);
  return encode(value, dcborEncodeOptions);
}

export function loadCanonical(bytes: Uint8Array): unknown {
  return decode(bytes);
}

function rejectNonCanonicalFloats(value: unknown): void {
  if (typeof value === "number") {
    if (Number.isNaN(value) || !Number.isFinite(value)) {
      throw new Error(
        "canonical CBOR does not accept NaN / ±∞ " +
          "(cross-language byte-equality is under-specified); " +
          "use null for absent values.",
      );
    }
    return;
  }
  if (Array.isArray(value)) {
    for (const v of value) rejectNonCanonicalFloats(v);
    return;
  }
  if (value && typeof value === "object") {
    for (const v of Object.values(value)) rejectNonCanonicalFloats(v);
  }
}
