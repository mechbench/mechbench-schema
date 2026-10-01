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


@pytest.mark.parametrize("leaf", ["d", "t1", "t123", "base", "my_axis-2", "d.cbor"])
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
        f"~scratch/{LIVE}/d..cbor",
        f"~scratch/{LIVE}/~hash",
        f"~scratch/LIVE_X/d",
        f"benji/mechbench/~scratch/{LIVE}",
    ],
)
def test_a_scratch_path_is_exactly_three_named_segments(path):
    with pytest.raises(InvalidPathError):
        parse_path(path)


@pytest.mark.parametrize(
    "path",
    [
        "benji/mechbench/results/j_d9m3t827h5yyx18kg57k/nodes/train.checkpoints",
        "benji/mechbench/adapters/l23/shards/adapters.safetensors",
        "benji/mechbench/merged/shards/model-00001-of-00002.safetensors",
        "benji/mechbench/checkpoints/l23-merged/config.json",
        "~system/renders/0f3a9c2e.png",
    ],
)
def test_a_dot_inside_a_segment_is_legal(path):
    parse_path(path)


@pytest.mark.parametrize(
    "path",
    [
        "benji/mechbench/a..b",
        "benji/mechbench/..",
        "benji/mechbench/shards/model..safetensors",
    ],
)
def test_a_doubled_dot_is_refused_by_name(path):
    with pytest.raises(InvalidPathError, match="dotdot"):
        parse_path(path)


@pytest.mark.parametrize(
    "path",
    [
        "benji/mechbench/.hidden",
        "benji/mechbench/name.",
        "benji/mechbench/.",
        "benji/mechbench/Adapters.safetensors",
        f"benji/mechbench/{'x' * 60}.bin",
    ],
)
def test_a_leading_trailing_or_uppercase_dotted_segment_is_refused(path):
    with pytest.raises(InvalidPathError):
        parse_path(path)
