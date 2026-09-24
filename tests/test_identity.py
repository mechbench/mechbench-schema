"""Path grammar: a hash segment is recognised before the named-segment rules."""

import pytest

from mechbench_schema.identity import (
    InvalidPathError,
    make_global_hash_path,
    make_scoped_hash_path,
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
