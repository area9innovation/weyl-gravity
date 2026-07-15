#!/usr/bin/env python3
"""Audit the conformal publications from an isolated tracked Git snapshot.

The audit never builds from the caller's working tree.  It archives a Git
tree-ish into a temporary directory, checks that every publication entrypoint
and recursively referenced TeX input belongs to that snapshot, verifies the
active generated input, builds all four publication artifacts to reference
stability, and runs the focused independent/provenance checks used for release
review.

This is a publication audit, not a replacement for the exhaustive theorem
rail.  The latter remains ``verify_conformal_paper_free.py --reproduce``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from typing import Any


PROJECT = Path(__file__).resolve().parents[1]
GIT_ROOT = Path(
    subprocess.run(
        ["git", "-C", str(PROJECT), "rev-parse", "--show-toplevel"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()
)
PROJECT_REL = PROJECT.relative_to(GIT_ROOT)

PUBLICATIONS = (
    "paper/07-conformal-residual-cohomology-krein.tex",
    "paper/08-conformal-covariant-causal-transport.tex",
    "paper/07-08-conformal-residual-cohomology-computational-supplement.tex",
    "paper/07-08-conformal-residual-cohomology-archive.tex",
)
TRACKED_PDFS = tuple(path[:-4] + ".pdf" for path in PUBLICATIONS)
ACTIVE_GENERATED_INPUT = "paper/generated/endpoint_factorization_nullstellensatz.tex"
ARCHIVE_PATHS = (
    ".github/workflows/conformal-bridge.yml",
    ".github/workflows/paper-naming.yml",
    str(PROJECT_REL),
)

INPUT_RE = re.compile(r"\\(?:input|include)\s*\{([^}]+)\}")
BAD_TEX_MARKERS = (
    "LaTeX Error",
    "undefined references",
    "Citation `",
    "Reference `",
    "Rerun to get cross-references right",
)


def run(
    command: list[str],
    *,
    cwd: Path,
    timeout: int,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    started = time.monotonic()
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        check=False,
    )
    elapsed = time.monotonic() - started
    if result.returncode != 0:
        raise RuntimeError(
            f"command failed ({result.returncode}): {' '.join(command)}\n"
            + result.stdout[-8000:]
        )
    return {
        "command": command,
        "elapsed_seconds": round(elapsed, 3),
        "output_tail": result.stdout[-2000:],
    }


def git_lines(*args: str) -> tuple[str, ...]:
    result = subprocess.run(
        ["git", "-C", str(GIT_ROOT), *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return tuple(line for line in result.stdout.splitlines() if line)


def strip_tex_comments(text: str) -> str:
    output: list[str] = []
    for line in text.splitlines():
        cut = len(line)
        for index, character in enumerate(line):
            if character != "%":
                continue
            backslashes = 0
            cursor = index - 1
            while cursor >= 0 and line[cursor] == "\\":
                backslashes += 1
                cursor -= 1
            if backslashes % 2 == 0:
                cut = index
                break
        output.append(line[:cut])
    return "\n".join(output)


def resolve_tex_inputs(
    project: Path, entrypoints: tuple[str, ...]
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    visited: set[Path] = set()
    active_inputs: set[Path] = set()

    def visit(source: Path) -> None:
        source = source.resolve()
        if source in visited:
            return
        if not source.is_file():
            raise FileNotFoundError(f"TeX source is absent: {source}")
        try:
            source.relative_to(project.resolve())
        except ValueError as error:
            raise RuntimeError(f"TeX source escapes project snapshot: {source}") from error
        visited.add(source)
        content = strip_tex_comments(source.read_text(encoding="utf-8"))
        for raw in INPUT_RE.findall(content):
            raw = raw.strip()
            candidate = source.parent / raw
            if candidate.suffix == "":
                candidate = candidate.with_suffix(".tex")
            candidate = candidate.resolve()
            if not candidate.is_file():
                raise FileNotFoundError(
                    f"unresolved TeX input {raw!r} from {source.relative_to(project)}"
                )
            active_inputs.add(candidate)
            visit(candidate)

    for entrypoint in entrypoints:
        visit(project / entrypoint)
    relative_visited = tuple(
        sorted(str(path.relative_to(project.resolve())) for path in visited)
    )
    relative_inputs = tuple(
        sorted(str(path.relative_to(project.resolve())) for path in active_inputs)
    )
    return relative_visited, relative_inputs


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_tex(project: Path, relative_source: str, timeout: int) -> dict[str, Any]:
    paper = project / "paper"
    name = Path(relative_source).name
    env = dict(os.environ)
    # Stabilize TeX timestamps within the isolated audit.  The tracked PDF is
    # retained as the submitted artifact; this audit proves clean rebuildability.
    env.setdefault("SOURCE_DATE_EPOCH", "946684800")
    passes = []
    # The archival monolith's contents and forward references can need one
    # pass beyond the conventional source/resolve pair after a clean export.
    for _ in range(3):
        record = run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "-file-line-error",
                name,
            ],
            cwd=paper,
            timeout=timeout,
            env=env,
        )
        # Undefined-reference and rerun notices are expected on intermediate
        # passes of a clean build.  ``pdflatex`` already fails hard errors;
        # warning discipline is checked against the final stabilized log.
        passes.append(record)
    pdf = paper / (Path(name).stem + ".pdf")
    if not pdf.is_file() or pdf.stat().st_size == 0:
        raise RuntimeError(f"reference-stable build did not create {pdf.name}")
    log = paper / (Path(name).stem + ".log")
    log_text = log.read_text(encoding="utf-8", errors="replace")
    bad = [marker for marker in BAD_TEX_MARKERS if marker in log_text]
    if bad:
        raise RuntimeError(f"{name} final log has release-blocking warnings: {bad}")
    return {
        "source": relative_source,
        "pdf": str(pdf.relative_to(project)),
        "pdf_sha256": sha256(pdf),
        "pdf_bytes": pdf.stat().st_size,
        "passes": passes,
    }


def archive_snapshot(treeish: str, destination: Path) -> tuple[str, set[str]]:
    commit = git_lines("rev-parse", "--verify", f"{treeish}^{{commit}}")[0]
    tracked = set(git_lines("ls-tree", "-r", "--name-only", treeish, "--", *ARCHIVE_PATHS))
    required = {
        str(PROJECT_REL / path) for path in (*PUBLICATIONS, *TRACKED_PDFS)
    }
    required.add(str(PROJECT_REL / ACTIVE_GENERATED_INPUT))
    missing = sorted(required - tracked)
    if missing:
        raise RuntimeError(
            "release tree is missing required tracked publication files:\n  "
            + "\n  ".join(missing)
        )

    archive = destination / "snapshot.tar"
    with archive.open("wb") as handle:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(GIT_ROOT),
                "archive",
                "--format=tar",
                treeish,
                *ARCHIVE_PATHS,
            ],
            stdout=handle,
            stderr=subprocess.PIPE,
            check=False,
        )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace"))
    extracted = destination / "snapshot"
    extracted.mkdir()
    with tarfile.open(archive) as payload:
        payload.extractall(extracted, filter="data")
    return commit, tracked


def audit(treeish: str, timeout: int) -> dict[str, Any]:
    if shutil.which("pdflatex") is None:
        raise RuntimeError("pdflatex is required for the clean publication audit")
    with tempfile.TemporaryDirectory(prefix="conformal-release-audit-") as raw_temp:
        temp = Path(raw_temp)
        commit, tracked = archive_snapshot(treeish, temp)
        snapshot_root = temp / "snapshot"
        project = snapshot_root / PROJECT_REL
        project_prefix = str(PROJECT_REL) + "/"
        tracked_project = tuple(
            sorted(path[len(project_prefix) :] for path in tracked if path.startswith(project_prefix))
        )
        tracked_inventory = temp / "tracked-project-files.txt"
        tracked_inventory.write_text("\n".join(tracked_project) + "\n", encoding="utf-8")
        check_env = dict(os.environ)
        check_env["CONFORMAL_TRACKED_FILES"] = str(tracked_inventory)

        visited, active_inputs = resolve_tex_inputs(project, PUBLICATIONS)
        active_git_paths = {str(PROJECT_REL / path) for path in active_inputs}
        untracked_inputs = sorted(active_git_paths - tracked)
        if untracked_inputs:
            raise RuntimeError(
                "active TeX inputs are not tracked in the release tree:\n  "
                + "\n  ".join(untracked_inputs)
            )
        if ACTIVE_GENERATED_INPUT not in active_inputs:
            raise RuntimeError(
                f"expected generated input is not active: {ACTIVE_GENERATED_INPUT}"
            )

        checks = []
        check_commands = (
            [sys.executable, "symbolic/generate_endpoint_factorization_nullstellensatz_tex.py", "--check"],
            [sys.executable, "symbolic/verify_conformal_residual_rank53_independent.py"],
            [sys.executable, "symbolic/verify_conformal_split_publications.py"],
            [sys.executable, "symbolic/verify_conformal_certificate_provenance.py"],
            [sys.executable, "symbolic/verify_conformal_covariant_H4_proof_ledger.py", "--check", "--guards"],
            [sys.executable, "-m", "unittest", "covariant_completion.final_transport.tests.test_proof_ledger"],
            [sys.executable, "symbolic/update_conformal_paper_snapshot.py", "--check"],
        )
        for command in check_commands:
            checks.append(run(command, cwd=project, timeout=timeout, env=check_env))

        builds = [build_tex(project, source, timeout) for source in PUBLICATIONS]
        return {
            "schema": "conformal-publication-clean-release-audit-v1",
            "treeish": treeish,
            "commit": commit,
            "isolated_git_archive": True,
            "working_tree_used_for_build": False,
            "publication_entrypoints": list(PUBLICATIONS),
            "recursively_visited_tex": list(visited),
            "active_tex_inputs": list(active_inputs),
            "active_generated_input": ACTIVE_GENERATED_INPUT,
            "focused_checks": checks,
            "reference_stable_builds": builds,
            "status": "PASS",
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tree-ish", default="HEAD")
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument(
        "--receipt",
        type=Path,
        help="optional JSON receipt path (relative paths resolve from project root)",
    )
    args = parser.parse_args()

    receipt = args.receipt
    if receipt is not None and not receipt.is_absolute():
        receipt = PROJECT / receipt
    result = audit(args.tree_ish, args.timeout)
    if receipt is not None:
        receipt.parent.mkdir(parents=True, exist_ok=True)
        receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("wrote", receipt)
    print("CONFORMAL PUBLICATION CLEAN RELEASE AUDIT: ALL PASS")
    print("tree:", result["commit"])
    print("publications:", len(result["publication_entrypoints"]))
    print("active TeX inputs:", len(result["active_tex_inputs"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
