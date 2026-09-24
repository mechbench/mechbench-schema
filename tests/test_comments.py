from __future__ import annotations

import ast
import io
import json
import re
import tokenize
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCHEMA_JSON = REPO / "ts" / "src" / "schema.json"

PYTHON_FILES = sorted(
    p
    for d in ("src", "scripts", "tests")
    for p in (REPO / d).rglob("*.py")
    if "__pycache__" not in p.parts and ".egg-info" not in str(p)
)
HAND_WRITTEN_TS = sorted(
    p
    for p in (REPO / "ts" / "src").rglob("*")
    if p.suffix in {".ts", ".mjs", ".js"} and p.name != "generated.ts"
)

DIRECTIVE = re.compile(
    r"#\s*(noqa\b|type:\s*ignore|pragma\b|fmt:|pyright:|mypy:|pylint:|ruff:|-\*-\s*coding|external:)"
)
TS_DIRECTIVE = re.compile(
    r"^(//|/\*)\s*(@ts-|eslint-|prettier-ignore|external:)|^///\s*<reference"
)
TASK_ID = re.compile(r"\b0\d{5}\b|(?i:\b(?:task|epic)\s+#?\d{3,})")
SKIP_DIRS = {".git", "node_modules", "dist", "__pycache__", ".venv", ".pytest_cache"}
PRIVATE_REPO = "eval" + "creativity"


def _rel(p: Path) -> str:
    return str(p.relative_to(REPO))


def _published_names() -> set[str]:
    return set(json.loads(SCHEMA_JSON.read_text())["$defs"])


def _text_files() -> list[Path]:
    out = []
    for p in REPO.rglob("*"):
        if not p.is_file() or SKIP_DIRS & set(p.parts) or ".egg-info" in str(p):
            continue
        if p.name in {"CHANGELOG.md", "package-lock.json"}:
            continue
        if p.suffix in {".py", ".md", ".ts", ".mjs", ".js", ".json", ".toml", ".yml", ".yaml", ".txt", ""}:
            out.append(p)
    return out


@pytest.mark.parametrize("path", PYTHON_FILES, ids=_rel)
def test_python_comments_are_directives_or_external(path: Path) -> None:
    tokens = tokenize.generate_tokens(io.StringIO(path.read_text()).readline)
    bad = [
        f"{_rel(path)}:{tok.start[0]}: {tok.string}"
        for tok in tokens
        if tok.type == tokenize.COMMENT
        and not (tok.start[0] == 1 and tok.string.startswith("#!"))
        and not DIRECTIVE.match(tok.string)
    ]
    assert not bad, "comments other than directives and `# external:`:\n" + "\n".join(bad)


@pytest.mark.parametrize("path", PYTHON_FILES, ids=_rel)
def test_python_docstrings_only_on_published_models(path: Path) -> None:
    published = _published_names() if "src" in path.relative_to(REPO).parts[:1] else set()
    tree = ast.parse(path.read_text())
    bad = []

    def bare_strings(body: list[ast.stmt]) -> list[ast.Expr]:
        return [
            s for s in body
            if isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant)
            and isinstance(s.value.value, str)
        ]

    for s in bare_strings(tree.body):
        bad.append(f"{_rel(path)}:{s.lineno}: module-level string")
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for s in bare_strings(node.body):
                bad.append(f"{_rel(path)}:{s.lineno}: string in {node.name}()")
        elif isinstance(node, ast.ClassDef):
            strings = bare_strings(node.body)
            for i, s in enumerate(strings):
                is_docstring = i == 0 and node.body[0] is s
                if not (is_docstring and node.name in published):
                    bad.append(f"{_rel(path)}:{s.lineno}: string in class {node.name}")
    assert not bad, "docstrings outside published models:\n" + "\n".join(bad)


@pytest.mark.parametrize("path", HAND_WRITTEN_TS, ids=_rel)
def test_typescript_comments_are_directives_or_external(path: Path) -> None:
    src = path.read_text()
    bad, i, line = [], 0, 1
    while i < len(src):
        c = src[i]
        if c == "\n":
            line += 1
        if c in "\"'`":
            j = i + 1
            while j < len(src) and src[j] != c:
                j += 2 if src[j] == "\\" else 1
            line += src[i:j].count("\n")
            i = j + 1
            continue
        if src.startswith("//", i) or src.startswith("/*", i):
            end = src.find("\n", i) if src[i + 1] == "/" else src.find("*/", i) + 2
            end = len(src) if end <= 0 else end
            text = src[i:end]
            if not TS_DIRECTIVE.match(text):
                bad.append(f"{_rel(path)}:{line}: {text.splitlines()[0]}")
            line += text.count("\n")
            i = end
            continue
        i += 1
    assert not bad, "comments other than directives and `// external:`:\n" + "\n".join(bad)


def test_no_task_id_outside_the_changelog() -> None:
    bad = [
        f"{_rel(p)}:{n}: {line.strip()[:100]}"
        for p in _text_files()
        for n, line in enumerate(p.read_text(errors="replace").splitlines(), 1)
        if TASK_ID.search(line)
    ]
    assert not bad, "task ids:\n" + "\n".join(bad)


def test_no_mention_of_the_private_experiments_repo() -> None:
    bad = [_rel(p) for p in _text_files() if PRIVATE_REPO in p.read_text(errors="replace").lower()]
    assert not bad, bad
