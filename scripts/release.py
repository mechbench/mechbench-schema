#!/usr/bin/env python3
"""The release gate (task 000300), schema edition.

Same contract as compute's and the runner's: no upload until the suite
is green, the wheel builds, and the wheel installs into a FRESH venv
with every dependency resolved from the real index — then a smoke that
exercises what a consumer does on a machine that has nothing else.

One check is specific to this repo: the generated TypeScript must match
fresh codegen output. `ts/src/generated.ts` and `ts/src/schema.json` are
derived files, and a release that ships Python models the TS bindings
do not know about is exactly the drift this package exists to prevent.

Usage:
    python scripts/release.py              # gate, then upload
    python scripts/release.py --dry-run    # gate only
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GENERATED = ("ts/src/schema.json", "ts/src/generated.ts")


def run(cmd: list[str], *, env: dict | None = None,
        timeout: float = 1800.0) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, cwd=str(REPO), env=env, capture_output=True, text=True,
        timeout=timeout, check=False,
    )


def die(step: str, proc: subprocess.CompletedProcess | None = None) -> None:
    print(f"\nRELEASE BLOCKED at: {step}")
    if proc is not None:
        print((((proc.stdout or "") + (proc.stderr or "")).strip())[-2000:])
    sys.exit(1)


def main() -> None:
    dry = "--dry-run" in sys.argv
    m = re.search(r'^version = "([^"]+)"',
                  (REPO / "pyproject.toml").read_text(), re.MULTILINE)
    if not m:
        die("reading version")
    ver = m.group(1)
    init = (REPO / "src" / "mechbench_schema" / "__init__.py").read_text()
    m2 = re.search(r'^__version__ = "([^"]+)"', init, re.MULTILINE)
    if not m2 or m2.group(1) != ver:
        die(f"version drift: pyproject says {ver}, __init__ says "
            f"{m2.group(1) if m2 else '(none)'}")
    print(f"gating mechbench-schema {ver}")

    print("[1/5] pytest")
    proc = run([sys.executable, "-m", "pytest", "tests/", "-q"])
    if proc.returncode != 0:
        die("pytest", proc)

    print("[2/5] codegen drift")
    before = {p: (REPO / p).read_text() for p in GENERATED}
    proc = run([sys.executable, "scripts/codegen.py"])
    if proc.returncode != 0:
        die("codegen", proc)
    drifted = [p for p in GENERATED if (REPO / p).read_text() != before[p]]
    if drifted:
        die(f"generated files are stale: {', '.join(drifted)} — "
            "run scripts/codegen.py and commit the result")

    print("[3/5] build")
    run(["rm", "-rf", str(REPO / "dist")])
    proc = run(["uv", "build"])
    if proc.returncode != 0:
        die("uv build", proc)
    wheels = sorted((REPO / "dist").glob("mechbench_schema-*.whl"))
    if not wheels:
        die("no wheel produced")

    with tempfile.TemporaryDirectory(prefix="schema-gate-") as td:
        tmp = Path(td)
        venv = tmp / "venv"
        home = tmp / "home"
        home.mkdir()
        print("[4/5] fresh venv install (deps from the real index)")
        proc = run(["uv", "venv", str(venv)])
        if proc.returncode != 0:
            die("uv venv", proc)
        proc = run(["uv", "pip", "install", "--refresh", "--python",
                    str(venv / "bin" / "python"), str(wheels[-1])])
        if proc.returncode != 0:
            die("uv pip install", proc)

        py = str(venv / "bin" / "python")
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(("MECHBENCH_", "HF_"))}
        env["HOME"] = str(home)

        print("[5/5] smoke: what a consumer does first")
        checks = [
            ("imports", "import mechbench_schema"),
            ("version is real",
             ("import mechbench_schema as m; "
              f"assert m.__version__ == {ver!r}, m.__version__")),
            ("the canonical codec round-trips",
             ("from mechbench_schema import dump_canonical, load_raw; "
              "assert load_raw(dump_canonical({'b': 1, 'a': [2, 3]})) "
              "== {'b': 1, 'a': [2, 3]}")),
            ("every exported name resolves",
             ("import mechbench_schema as m; "
              "missing = [n for n in m.__all__ if not hasattr(m, n)]; "
              "assert not missing, missing")),
        ]
        for name, code in checks:
            proc = run([py, "-c", code], env=env, timeout=120)
            if proc.returncode != 0:
                die(f"smoke: {name}", proc)

    print(f"\ngate PASSED for {ver}")
    if dry:
        print("dry run — not uploading")
        return
    print("uploading…")
    proc = run(["uvx", "twine", "upload", f"dist/mechbench_schema-{ver}*"],
               timeout=600)
    if proc.returncode != 0:
        die("twine upload", proc)
    print(f"published mechbench-schema {ver}")


if __name__ == "__main__":
    main()
