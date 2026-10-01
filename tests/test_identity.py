import pytest

from mechbench_schema.identity import (
    InvalidPathError,
    make_global_hash_path,
    make_scoped_hash_path,
    make_scratch_path,
    RESERVED_ROOTS,
    parse_path,
)

SHA256 = "a" * 64
SHA512 = "b" * 128


def test_a_sha256_global_hash_path_is_valid():
    path = make_global_hash_path("sha256", SHA256)
    assert parse_path(path).category == "global_hash"


def test_a_sha256_scoped_hash_path_is_valid():
    path = make_scoped_hash_path("benji", "mechbench", "sha256", SHA256)
    assert parse_path(path).category == "scoped_hash"


def test_a_sha512_hash_segment_is_valid():
    assert parse_path(make_global_hash_path("sha512", SHA512)).category == "global_hash"


def test_a_named_segment_keeps_its_63_character_limit():
    with pytest.raises(InvalidPathError, match="63-char"):
        parse_path(f"benji/mechbench/{'x' * 64}")


def test_a_hash_segment_has_its_own_limit():
    with pytest.raises(InvalidPathError, match="145-char"):
        parse_path(f"~hash/sha256:{'c' * 200}")


def test_a_colon_outside_a_hash_segment_is_still_refused():
    with pytest.raises(InvalidPathError):
        parse_path("benji/mechbench/not:a-hash")


LIVE = "live_7k2m9q4r8t1v5x3z6b0c"


def test_scratch_is_a_reserved_root():
    assert "~scratch" in RESERVED_ROOTS


@pytest.mark.parametrize("leaf", ["d", "t1", "t123", "base", "my_axis-2"])
def test_a_scratch_path_names_its_live_run_and_leaf(leaf):
    parsed = parse_path(make_scratch_path(LIVE, leaf))
    assert parsed.category == "scratch"
    assert parsed.live_run_id == LIVE
    assert parsed.leaf == leaf
    assert parsed.owner is None and parsed.project is None


@pytest.mark.parametrize(
    "path",
    [
        "~scratch",
        f"~scratch/{LIVE}",
        f"~scratch/{LIVE}/a/b",
        f"~scratch/{LIVE}/t1/x",
        f"~scratch/{LIVE}/T1",
        f"~scratch/{LIVE}/d.cbor",
        f"~scratch/{LIVE}/~hash",
        f"~scratch/LIVE_X/d",
        f"benji/mechbench/~scratch/{LIVE}",
    ],
)
def test_a_scratch_path_is_exactly_three_named_segments(path):
    with pytest.raises(InvalidPathError):
        parse_path(path)
