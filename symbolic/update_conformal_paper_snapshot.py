#!/usr/bin/env python3
"""Generate or verify the conformal-paper dependency hash manifest."""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "symbolic" / "conformal-paper-verification.sha256"
ALLOWED_SUFFIXES = {".py", ".json", ".tex", ".md", ".tsv"}


def display_path(path: Path) -> Path:
    """Return the manifest path relative to the project directory."""

    return Path(os.path.relpath(path, ROOT))


def dependencies() -> tuple[Path, ...]:
    files: set[Path] = {
        ROOT.parent.parent / ".github" / "workflows" / "conformal-bridge.yml",
        ROOT / "README.md",
        ROOT / "notes" / "conformal-paper-snapshot.md",
        ROOT / "notes" / "conformal-publication-reproduction.md",
        ROOT / "paper" / "conformal-residual-cohomology.tex",
        ROOT / "paper" / "conformal-residual-cohomology.pdf",
        ROOT / "paper" / "ghosts-geometry-reality.tex",
        ROOT / "paper" / "ghosts-geometry-reality.pdf",
        ROOT / "symbolic" / "conformal-paper-requirements.txt",
        Path(__file__).resolve(),
    }
    for directory in (
        "bridge",
        "field_bv_identification",
        "analytic_completion",
        "covariant_completion",
    ):
        for path in (ROOT / directory).rglob("*"):
            if path.is_file() and path.suffix in ALLOWED_SUFFIXES and "__pycache__" not in path.parts:
                files.add(path)
    files.update((ROOT / "symbolic").glob("verify_conformal_*.py"))
    return tuple(sorted(files, key=lambda path: str(display_path(path))))


def manifest_text() -> str:
    rows = []
    for path in dependencies():
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append(f"{digest}  {display_path(path)}")
    return "\n".join(rows) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = manifest_text()
    if args.write:
        MANIFEST.write_text(expected, encoding="utf-8")
        print("wrote", MANIFEST.relative_to(ROOT), f"({len(dependencies())} files)")
    if args.check:
        if not MANIFEST.exists() or MANIFEST.read_text(encoding="utf-8") != expected:
            raise SystemExit("conformal paper dependency manifest is stale; run --write")
        print("CONFORMAL PAPER DEPENDENCY SNAPSHOT: ALL PASS")
    if not args.write and not args.check:
        print(expected, end="")


if __name__ == "__main__":
    main()
