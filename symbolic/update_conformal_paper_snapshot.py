#!/usr/bin/env python3
"""Generate or verify the conformal-paper dependency hash manifest."""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "symbolic" / "conformal-paper-verification.sha256"
ALLOWED_SUFFIXES = {".py", ".json", ".tex", ".md", ".tsv"}
TRACKED_FILES_ENV = "CONFORMAL_TRACKED_FILES"
RECURSIVE_ROOTS = (
    "bridge",
    "field_bv_identification",
    "analytic_completion",
    "covariant_completion",
)


def display_path(path: Path) -> Path:
    """Return the manifest path relative to the project directory."""

    return Path(os.path.relpath(path, ROOT))


def _manifest_fallback_paths() -> tuple[str, ...]:
    """Use the frozen path inventory when checking an exported source archive."""

    if not MANIFEST.is_file():
        raise RuntimeError(
            "tracked-file inventory unavailable: run inside Git or set "
            f"{TRACKED_FILES_ENV}"
        )
    output = []
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if "  " not in line:
            continue
        relative = line.split("  ", 1)[1]
        path = (ROOT / relative).resolve()
        try:
            output.append(str(path.relative_to(ROOT.resolve())))
        except ValueError:
            continue
    return tuple(output)


def tracked_project_paths() -> tuple[str, ...]:
    """Return project-relative tracked paths without admitting dirty extras."""

    inventory = os.environ.get(TRACKED_FILES_ENV)
    if inventory:
        return tuple(
            line
            for line in Path(inventory).read_text(encoding="utf-8").splitlines()
            if line
        )
    result = subprocess.run(
        [
            "git",
            "-C",
            str(ROOT),
            "ls-files",
            "-z",
            "--",
            *RECURSIVE_ROOTS,
            "symbolic",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode == 0:
        return tuple(
            entry.decode("utf-8")
            for entry in result.stdout.split(b"\0")
            if entry
        )
    return _manifest_fallback_paths()


def dependencies() -> tuple[Path, ...]:
    files: set[Path] = {
        ROOT.parent.parent / ".github" / "workflows" / "conformal-bridge.yml",
        ROOT / "README.md",
        ROOT / "notes" / "conformal-paper-snapshot.md",
        ROOT / "notes" / "conformal-paper-split-roadmap.md",
        ROOT / "notes" / "conformal-referee-major-revision.md",
        ROOT / "notes" / "conformal-publication-reproduction.md",
        ROOT / "paper" / "conformal-residual-cohomology.tex",
        ROOT / "paper" / "conformal-residual-cohomology.pdf",
        ROOT / "paper" / "conformal-residual-cohomology-krein.tex",
        ROOT / "paper" / "conformal-residual-cohomology-krein.pdf",
        ROOT / "paper" / "conformal-covariant-causal-transport.tex",
        ROOT / "paper" / "conformal-covariant-causal-transport.pdf",
        ROOT / "paper" / "conformal-residual-cohomology-computational-supplement.tex",
        ROOT / "paper" / "conformal-residual-cohomology-computational-supplement.pdf",
        ROOT / "paper" / "generated" / "endpoint_factorization_nullstellensatz.tex",
        ROOT / "paper" / "ghosts-geometry-reality.tex",
        ROOT / "paper" / "ghosts-geometry-reality.pdf",
        ROOT / "symbolic" / "conformal-paper-requirements.txt",
        ROOT / "symbolic" / "audit_conformal_publication_release.py",
        ROOT / "symbolic" / "generate_endpoint_factorization_nullstellensatz_tex.py",
        ROOT / "symbolic" / "programme-introduction-language-report.json",
        ROOT / "symbolic" / "programme-introduction-language-report.tsv",
        ROOT / "symbolic" / "programme-introduction-verification.sha256",
        ROOT / "symbolic" / "verify_programme_introduction.py",
        ROOT / "symbolic" / "verify_conformal_split_publications.py",
        Path(__file__).resolve(),
    }
    for relative in tracked_project_paths():
        path = ROOT / relative
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        if relative.startswith(RECURSIVE_ROOTS) and path.suffix in ALLOWED_SUFFIXES:
            files.add(path)
        elif Path(relative).parent == Path("symbolic") and Path(relative).name.startswith(
            "verify_conformal_"
        ) and path.suffix == ".py":
            files.add(path)
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
