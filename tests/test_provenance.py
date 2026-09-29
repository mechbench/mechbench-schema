import pytest

from mechbench_schema import Emitted, ExtensionPin, Provenance

BASE = {"created_at": "2026-09-29T00:00:00Z",
        "produced_by": {"tool": "mechbench-compute", "version": "0.166.0"},
        "schema_version": "0.18.0",
        "operation": "~canonical/ops/records/filter"}

PIN = {"address": "alice/interp-extras/extensions/interp-extras", "version": 2,
       "hash": "sha256:" + "a" * 64}


def test_a_core_operations_provenance_has_no_extension_and_dumps_as_before():
    got = Provenance.model_validate(BASE)
    assert got.extension is None
    assert "extension" not in got.model_dump() and "extension" not in got.model_dump(mode="json")
    assert Emitted(provenance=got, payload={}).model_dump()["provenance"] == {
        **BASE, "inputs": [], "params_fingerprint": None, "fidelity": None, "params_ref": None}


def test_an_extension_operations_provenance_carries_the_pin():
    got = Provenance.model_validate({**BASE, "operation": "alice/interp-extras/ops/geometry/align",
                                     "extension": PIN})
    assert got.extension == ExtensionPin(**PIN)
    assert got.model_dump(mode="json")["extension"] == PIN


@pytest.mark.parametrize("bad", [{**PIN, "hash": "sha256:short"}, {**PIN, "version": 0},
                                 {**PIN, "address": "not a path"}])
def test_a_malformed_pin_is_refused(bad):
    with pytest.raises(ValueError):
        Provenance.model_validate({**BASE, "extension": bad})
