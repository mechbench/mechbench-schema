from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Annotated, Literal

from pydantic import AfterValidator, Field


_SEGMENT_PATTERN = r"[a-z0-9](?:[a-z0-9_-]{0,61}[a-z0-9])?"
_SEGMENT_RE = re.compile(f"^{_SEGMENT_PATTERN}$")

_HASH_PATTERN = r"(?P<algo>[a-z0-9]+):(?P<digest>[0-9a-f]+)"
_HASH_RE = re.compile(f"^{_HASH_PATTERN}$")

_INVALID_CHARS = set(" \\:?*<>|\"'#%\t\n\r")

RESERVED_ROOTS = frozenset({"~system", "~canonical", "~hash"})

RESERVED_SCOPED_PREFIXES = frozenset({"~hash"})

MAX_TOTAL_LENGTH = 255
MAX_SEGMENT_LENGTH = 63
MAX_HASH_SEGMENT_LENGTH = 145

PathCategory = Literal[
    "user_named",
    "canonical",
    "platform",
    "global_hash",
    "scoped_hash",
]


class InvalidPathError(ValueError):
    pass


def _validate_segment(segment: str, *, allow_hash: bool = False) -> None:
    if not segment:
        raise InvalidPathError("empty segment")
    if allow_hash and _HASH_RE.match(segment):
        if len(segment) > MAX_HASH_SEGMENT_LENGTH:
            raise InvalidPathError(
                f"hash segment {segment!r} exceeds {MAX_HASH_SEGMENT_LENGTH}-char limit"
            )
        return
    if len(segment) > MAX_SEGMENT_LENGTH:
        raise InvalidPathError(
            f"segment {segment!r} exceeds {MAX_SEGMENT_LENGTH}-char limit"
        )
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

    if len(segments) < 3:
        raise InvalidPathError(
            f"user-owned path {path!r} must have at least 3 segments "
            f"(<owner>/<project>/.../<leaf>)"
        )

    _validate_segment(first)
    _validate_segment(segments[1])

    rest = segments[2:]
    for i, seg in enumerate(rest):
        if seg.startswith("~"):
            if seg != "~hash":
                raise InvalidPathError(
                    f"segment {seg!r} in user-owned path {path!r} is not allowed; "
                    f"only ~hash is permitted inside a user/project path"
                )
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


MechbenchPath = Annotated[
    str,
    AfterValidator(_validate_mechbench_path),
    Field(
        description=(
            "A mechbench object id. "
            "Five categories: user-named (<owner>/<project>/.../<leaf>), "
            "canonical (~canonical/<area>/.../<leaf>), "
            "platform (~system/<area>/.../<leaf>), "
            "global content-hashed (~hash/<algo>:<digest>), "
            "and workspace-scoped content-hashed "
            "(<owner>/<project>/~hash/<algo>:<digest>)."
        ),
    ),
]


@dataclass(frozen=True)
class ParsedPath:
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
    _validate_mechbench_path(path)
    segments = path.split("/")
    first = segments[0]

    if first == "~hash":
        m = _HASH_RE.match(segments[1])
        assert m is not None
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

    if len(segments) >= 4 and segments[-2] == "~hash":
        m = _HASH_RE.match(segments[-1])
        assert m is not None
        return ParsedPath(
            raw=path,
            category="scoped_hash",
            owner=first,
            project=segments[1],
            hash_algo=m.group("algo"),
            hash_digest=m.group("digest"),
        )

    return ParsedPath(
        raw=path,
        category="user_named",
        owner=first,
        project=segments[1],
        folders=tuple(segments[2:-1]),
        leaf=segments[-1],
    )


def make_user_path(owner: str, project: str, *folders_and_leaf: str) -> str:
    if len(folders_and_leaf) < 1:
        raise InvalidPathError(
            "make_user_path requires at least one folder-or-leaf segment"
        )
    path = "/".join((owner, project, *folders_and_leaf))
    return _validate_mechbench_path(path)


def make_canonical_path(area: str, *subpath_and_leaf: str) -> str:
    if len(subpath_and_leaf) < 1:
        raise InvalidPathError(
            "make_canonical_path requires at least one subpath-or-leaf segment"
        )
    path = "/".join(("~canonical", area, *subpath_and_leaf))
    return _validate_mechbench_path(path)


def make_platform_path(area: str, *subpath_and_leaf: str) -> str:
    if len(subpath_and_leaf) < 1:
        raise InvalidPathError(
            "make_platform_path requires at least one subpath-or-leaf segment"
        )
    path = "/".join(("~system", area, *subpath_and_leaf))
    return _validate_mechbench_path(path)


def make_global_hash_path(algo: str, digest: str) -> str:
    path = f"~hash/{algo}:{digest}"
    return _validate_mechbench_path(path)


def make_scoped_hash_path(
    owner: str, project: str, algo: str, digest: str,
) -> str:
    path = f"{owner}/{project}/~hash/{algo}:{digest}"
    return _validate_mechbench_path(path)
