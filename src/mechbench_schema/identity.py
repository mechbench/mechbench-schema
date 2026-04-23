"""Mechbench object-id types and utilities.

Implements the identity scheme specified in
`mechbench/docs/IDENTITY_AND_NAMESPACING.md`. Five id categories:

  user_named   <owner>/<project>/.../<leaf>
  canonical    ~canonical/<area>/.../<leaf>
  platform     ~system/<area>/.../<leaf>
  global_hash  ~hash/<algo>:<digest>
  scoped_hash  <owner>/<project>/~hash/<algo>:<digest>

`MechbenchPath` is a Pydantic-validated string: any string field
typed as `MechbenchPath` is checked against the grammar on
construction. For programmatic construction use the `make_*`
helpers; for parsing into typed components use `parse_path`.

TS-side consumers see `MechbenchPath` as a plain `string` — JSON
Schema carries the pattern and a description. Parsing/construction
on the TS side is the UI's concern and lives in mechbench-ui.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Annotated, Literal

from pydantic import AfterValidator, Field

# --- Grammar constants ------------------------------------------------------

# Segment: lowercase alnum, internal hyphens/underscores, must start+end
# with alnum. Length 1-63.
_SEGMENT_PATTERN = r"[a-z0-9](?:[a-z0-9_-]{0,61}[a-z0-9])?"
_SEGMENT_RE = re.compile(f"^{_SEGMENT_PATTERN}$")

# Hash segment: <algo>:<hex-digest>. algo is lowercase alnum; digest is hex.
_HASH_PATTERN = r"(?P<algo>[a-z0-9]+):(?P<digest>[0-9a-f]+)"
_HASH_RE = re.compile(f"^{_HASH_PATTERN}$")

# Chars never allowed in any segment (superset of what _SEGMENT_RE rejects,
# listed here for explicit errors).
_INVALID_CHARS = set(" \\:?*<>|\"'#%\t\n\r")

# Platform-reserved top-level segments. User/org handles may not use these.
RESERVED_ROOTS = frozenset({"~system", "~canonical", "~hash"})

# Within a user/project path, this is the only `~`-prefixed segment allowed.
# E.g. `benji/mechbench/~hash/sha256:...` is valid; `benji/~system/...` is not.
RESERVED_SCOPED_PREFIXES = frozenset({"~hash"})

# Soft limits enforced by the validator.
MAX_TOTAL_LENGTH = 255
MAX_SEGMENT_LENGTH = 63

# Category names — stable literal strings used both in parsed output and in
# the UI for routing decisions.
PathCategory = Literal[
    "user_named",
    "canonical",
    "platform",
    "global_hash",
    "scoped_hash",
]


# --- Validation -------------------------------------------------------------


class InvalidPathError(ValueError):
    """Raised when a string does not satisfy the MechbenchPath grammar."""


def _validate_segment(segment: str, *, allow_hash: bool = False) -> None:
    if not segment:
        raise InvalidPathError("empty segment")
    if len(segment) > MAX_SEGMENT_LENGTH:
        raise InvalidPathError(
            f"segment {segment!r} exceeds {MAX_SEGMENT_LENGTH}-char limit"
        )
    # Hash segments (`<algo>:<digest>`) get validated against _HASH_RE first;
    # they legitimately contain `:` which _INVALID_CHARS would otherwise reject.
    if allow_hash and _HASH_RE.match(segment):
        return
    bad_chars = _INVALID_CHARS & set(segment)
    if bad_chars:
        raise InvalidPathError(
            f"segment {segment!r} contains invalid characters: {sorted(bad_chars)!r}"
        )
    if not _SEGMENT_RE.match(segment):
        raise InvalidPathError(
            f"segment {segment!r} does not match "
            f"[a-z0-9][a-z0-9_-]*[a-z0-9] (lowercase alnum + internal - / _)"
        )


def _validate_mechbench_path(path: str) -> str:
    if not isinstance(path, str):
        raise InvalidPathError(f"path must be str, got {type(path).__name__}")
    if not path:
        raise InvalidPathError("path must not be empty")
    if len(path) > MAX_TOTAL_LENGTH:
        raise InvalidPathError(
            f"path length {len(path)} exceeds {MAX_TOTAL_LENGTH}-char limit"
        )
    if path.startswith("/") or path.endswith("/") or "//" in path:
        raise InvalidPathError(f"path {path!r} has leading/trailing/repeated slashes")

    segments = path.split("/")
    first = segments[0]

    if first == "~hash":
        # Global hash: ~hash/<algo>:<digest> — exactly 2 segments.
        if len(segments) != 2:
            raise InvalidPathError(
                f"global-hash path {path!r} must be '~hash/<algo>:<digest>'"
            )
        _validate_segment(segments[1], allow_hash=True)
        if not _HASH_RE.match(segments[1]):
            raise InvalidPathError(
                f"global-hash path {path!r}: last segment must be <algo>:<digest>"
            )
        return path

    if first in {"~system", "~canonical"}:
        # Platform / canonical: ~<root>/<area>/.../<leaf> — at least 3 segments.
        if len(segments) < 3:
            raise InvalidPathError(
                f"{first} path {path!r} must have at least 3 segments"
            )
        for seg in segments[1:]:
            _validate_segment(seg)
        return path

    if first.startswith("~"):
        raise InvalidPathError(
            f"unknown platform-reserved root segment: {first!r}. "
            f"Known: {sorted(RESERVED_ROOTS)!r}"
        )

    # User-owned path: <owner>/<project>/.../<leaf>
    if len(segments) < 3:
        raise InvalidPathError(
            f"user-owned path {path!r} must have at least 3 segments "
            f"(<owner>/<project>/.../<leaf>)"
        )

    # Validate owner and project (no ~ allowed).
    _validate_segment(first)
    _validate_segment(segments[1])

    # Remaining segments: allow ~hash (with hash leaf) but no other ~prefixes.
    rest = segments[2:]
    for i, seg in enumerate(rest):
        if seg.startswith("~"):
            if seg != "~hash":
                raise InvalidPathError(
                    f"segment {seg!r} in user-owned path {path!r} is not allowed; "
                    f"only ~hash is permitted inside a user/project path"
                )
            # ~hash must be followed by exactly one hash-leaf segment.
            if i != len(rest) - 2:
                raise InvalidPathError(
                    f"~hash in user-owned path {path!r} must be "
                    f"immediately followed by a single <algo>:<digest> leaf"
                )
            hash_leaf = rest[i + 1]
            if not _HASH_RE.match(hash_leaf):
                raise InvalidPathError(
                    f"segment after ~hash in {path!r} must match <algo>:<digest>"
                )
            _validate_segment(hash_leaf, allow_hash=True)
            return path
        _validate_segment(seg)

    return path


# --- The type ---------------------------------------------------------------

MechbenchPath = Annotated[
    str,
    AfterValidator(_validate_mechbench_path),
    Field(
        description=(
            "A mechbench object id. See "
            "mechbench/docs/IDENTITY_AND_NAMESPACING.md for the full grammar. "
            "Five categories: user-named (<owner>/<project>/.../<leaf>), "
            "canonical (~canonical/<area>/.../<leaf>), "
            "platform (~system/<area>/.../<leaf>), "
            "global content-hashed (~hash/<algo>:<digest>), "
            "and workspace-scoped content-hashed "
            "(<owner>/<project>/~hash/<algo>:<digest>)."
        ),
    ),
]


# --- Parsing ----------------------------------------------------------------


@dataclass(frozen=True)
class ParsedPath:
    """Parsed components of a MechbenchPath.

    Fields populated depend on `category`:
      user_named:   owner, project, folders, leaf
      canonical:    area, area_path, leaf
      platform:     area, area_path, leaf
      global_hash:  hash_algo, hash_digest
      scoped_hash:  owner, project, hash_algo, hash_digest
    """

    raw: str
    category: PathCategory
    owner: str | None = None
    project: str | None = None
    folders: tuple[str, ...] = ()
    leaf: str | None = None
    area: str | None = None
    area_path: tuple[str, ...] = ()
    hash_algo: str | None = None
    hash_digest: str | None = None


def parse_path(path: str) -> ParsedPath:
    """Parse a path string into its typed components.

    Validates the path as a side effect; raises InvalidPathError if the
    path doesn't satisfy the grammar.
    """
    _validate_mechbench_path(path)
    segments = path.split("/")
    first = segments[0]

    if first == "~hash":
        m = _HASH_RE.match(segments[1])
        assert m is not None  # validator guarantees
        return ParsedPath(
            raw=path,
            category="global_hash",
            hash_algo=m.group("algo"),
            hash_digest=m.group("digest"),
        )

    if first == "~canonical":
        return ParsedPath(
            raw=path,
            category="canonical",
            area=segments[1],
            area_path=tuple(segments[2:-1]),
            leaf=segments[-1],
        )

    if first == "~system":
        return ParsedPath(
            raw=path,
            category="platform",
            area=segments[1],
            area_path=tuple(segments[2:-1]),
            leaf=segments[-1],
        )

    # User-owned: check for scoped-hash pattern.
    if len(segments) >= 4 and segments[-2] == "~hash":
        m = _HASH_RE.match(segments[-1])
        assert m is not None  # validator guarantees
        return ParsedPath(
            raw=path,
            category="scoped_hash",
            owner=first,
            project=segments[1],
            hash_algo=m.group("algo"),
            hash_digest=m.group("digest"),
        )

    # Plain user-named.
    return ParsedPath(
        raw=path,
        category="user_named",
        owner=first,
        project=segments[1],
        folders=tuple(segments[2:-1]),
        leaf=segments[-1],
    )


# --- Construction helpers ---------------------------------------------------


def make_user_path(owner: str, project: str, *folders_and_leaf: str) -> str:
    """Build a user-named path. The last positional arg is the leaf; the rest
    are intermediate folders. Validates the result."""
    if len(folders_and_leaf) < 1:
        raise InvalidPathError(
            "make_user_path requires at least one folder-or-leaf segment"
        )
    path = "/".join((owner, project, *folders_and_leaf))
    return _validate_mechbench_path(path)


def make_canonical_path(area: str, *subpath_and_leaf: str) -> str:
    """Build a canonical path: ~canonical/<area>/.../<leaf>."""
    if len(subpath_and_leaf) < 1:
        raise InvalidPathError(
            "make_canonical_path requires at least one subpath-or-leaf segment"
        )
    path = "/".join(("~canonical", area, *subpath_and_leaf))
    return _validate_mechbench_path(path)


def make_platform_path(area: str, *subpath_and_leaf: str) -> str:
    """Build a platform/system path: ~system/<area>/.../<leaf>."""
    if len(subpath_and_leaf) < 1:
        raise InvalidPathError(
            "make_platform_path requires at least one subpath-or-leaf segment"
        )
    path = "/".join(("~system", area, *subpath_and_leaf))
    return _validate_mechbench_path(path)


def make_global_hash_path(algo: str, digest: str) -> str:
    """Build a global content-hashed path: ~hash/<algo>:<digest>."""
    path = f"~hash/{algo}:{digest}"
    return _validate_mechbench_path(path)


def make_scoped_hash_path(
    owner: str, project: str, algo: str, digest: str,
) -> str:
    """Build a workspace-scoped content-hashed path:
    <owner>/<project>/~hash/<algo>:<digest>."""
    path = f"{owner}/{project}/~hash/{algo}:{digest}"
    return _validate_mechbench_path(path)
