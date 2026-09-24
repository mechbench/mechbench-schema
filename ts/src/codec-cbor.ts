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
