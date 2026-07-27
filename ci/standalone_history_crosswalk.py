#!/usr/bin/env python3
"""Derive and check the pre-extraction -> standalone commit crosswalk.

Background
----------
This repository was extracted from a monorepo subtree.  The extraction rewrote
every commit id and stripped the ``physics/symplectic-reconstruction/`` path
prefix.  Provenance pins of the form

    git show <OLD_COMMIT>:physics/symplectic-reconstruction/<path>

therefore resolve to nothing here.  The old commit ids are not recoverable from
this repository by lookup -- no filter-repo mapping table survived the split.

They are recoverable by *content*.  Each pin also records the sha256 its blob is
expected to have.  Strip the prefix, walk the commits that touched that path in
the filtered history, and find the one whose blob hashes to the recorded value:
that commit is the rewritten image of the old one.

This tool performs that derivation over every pin in the tree and writes an
explicit crosswalk, including a ledger of what it could *not* resolve.  It never
guesses: a pin whose recorded content appears nowhere is reported as unresolved.

Usage
-----
    python3 ci/standalone_history_crosswalk.py            # rebuild the crosswalk
    python3 ci/standalone_history_crosswalk.py --check    # fail on drift

``--check`` is the verifier rail.  It re-derives the mapping and compares it to
the committed artifact, so a stale or hand-edited crosswalk fails closed.

Runtime is a few minutes: it walks per-path history and hashes candidate blobs.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import pathlib
import re
import subprocess
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
ARTIFACT = ROOT / "reports" / "standalone-history-crosswalk.json"
PREFIX = "physics/symplectic-reconstruction/"

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
COMMITISH = re.compile(r"commit", re.I)

# Paths that belong to the external tango/forge substrate repository and were
# never part of this subtree.  Pins against them are expected to be
# unresolvable here and are classified rather than reported as damage.
EXTERNAL_PREFIXES = ("lib/math/", "forge/", "tools/science-forge/")

_touched: dict[str, list[str]] = {}
_blob: dict[tuple[str, str], str | None] = {}


def _git(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True)


def _commits_touching(path: str) -> list[str]:
    if path not in _touched:
        out = _git(["log", "--format=%H", "--all", "--", path]).stdout.decode()
        _touched[path] = out.split()
    return _touched[path]


def _blob_sha256(commit: str, path: str) -> str | None:
    key = (commit, path)
    if key not in _blob:
        r = _git(["show", f"{commit}:{path}"])
        _blob[key] = None if r.returncode else hashlib.sha256(r.stdout).hexdigest()
    return _blob[key]


def _strip(p: str) -> str:
    return p[len(PREFIX):] if p.startswith(PREFIX) else p


def _is_external(path: str) -> bool:
    return _strip(path).startswith(EXTERNAL_PREFIXES)


def _resolve(old_path: str, sha: str) -> tuple[str, str] | None:
    new_path = _strip(old_path)
    for c in _commits_touching(new_path):
        if _blob_sha256(c, new_path) == sha:
            return c, new_path
    return None


def _json_pins(rel: str, node, out: list, path: str = "") -> None:
    if isinstance(node, dict):
        ck = next((k for k in node
                   if COMMITISH.search(k) and isinstance(node[k], str)
                   and HEX40.match(node[k])), None)
        p, s = node.get("path"), node.get("sha256")
        if ck and isinstance(p, str) and isinstance(s, str) and HEX64.match(s):
            out.append({"site": f"{rel}::{path}", "old_commit": node[ck],
                        "old_path": p, "sha256": s})
        for k, v in node.items():
            _json_pins(rel, v, out, f"{path}/{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _json_pins(rel, v, out, f"{path}[{i}]")


def _py_pins(rel: str, text: str, out: list) -> None:
    """Module-level string constants, via ast so multi-line concatenation works."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return
    consts: dict[str, str] = {}
    for node in tree.body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)):
            try:
                value = ast.literal_eval(node.value)
            except Exception:
                continue
            if isinstance(value, str):
                consts[node.targets[0].id] = value
    commits = {k: v for k, v in consts.items() if HEX40.match(v)}
    paths = {k: v for k, v in consts.items() if PREFIX in v}
    shas = {k: v for k, v in consts.items() if HEX64.match(v)}
    # only the unambiguous single-triple case is claimed
    if len(commits) == 1 and len(paths) == 1 and len(shas) == 1:
        (ck, cv) = next(iter(commits.items()))
        out.append({"site": f"{rel}::{ck}", "old_commit": cv,
                    "old_path": next(iter(paths.values())),
                    "sha256": next(iter(shas.values()))})


def collect_pins() -> list[dict]:
    files = subprocess.run(["git", "ls-files"], cwd=ROOT,
                           capture_output=True, text=True).stdout.split()
    pins: list[dict] = []
    for rel in files:
        p = ROOT / rel
        if p.suffix == ".json":
            try:
                _json_pins(rel, json.loads(p.read_text(encoding="utf-8")), pins)
            except Exception:
                continue
        elif p.suffix == ".py":
            _py_pins(rel, p.read_text(encoding="utf-8", errors="ignore"), pins)
    return pins


def build() -> dict:
    pins = collect_pins()
    shas = sorted({q["old_commit"] for q in pins})
    checked = subprocess.run(
        ["git", "cat-file", "--batch-check"], cwd=ROOT, text=True,
        input="\n".join(s + "^{commit}" for s in shas),
        capture_output=True).stdout.strip().split("\n")
    alive = {s for s, line in zip(shas, checked) if " commit " in line}

    dangling = [q for q in pins if q["old_commit"] not in alive]
    by_commit: dict[str, list[dict]] = defaultdict(list)
    for q in dangling:
        by_commit[q["old_commit"]].append(q)

    mapping, unresolved, external = {}, [], []
    for old, group in sorted(by_commit.items()):
        hit = None
        for q in group:
            if _is_external(q["old_path"]):
                continue
            got = _resolve(q["old_path"], q["sha256"])
            if got:
                hit = (got, q)
                break
        if hit:
            (new_commit, new_path), q = hit
            mapping[old] = {
                "new_commit": new_commit,
                "witness_old_path": q["old_path"],
                "witness_new_path": new_path,
                "witness_sha256": q["sha256"],
                "sites": sorted({g["site"] for g in group}),
            }
        elif all(_is_external(g["old_path"]) for g in group):
            external.append({
                "old_commit": old,
                "paths": sorted({g["old_path"] for g in group}),
                "sites": sorted({g["site"] for g in group}),
                "reason": "pins the external tango/forge substrate repository, "
                          "which was never part of this subtree",
            })
        else:
            unresolved.append({
                "old_commit": old,
                "sites": sorted({g["site"] for g in group}),
                "tried": [{"path": g["old_path"], "sha256": g["sha256"]}
                          for g in group],
                "reason": "no commit in the filtered history holds this content "
                          "at this path",
            })

    return {
        "schema": "standalone-history-crosswalk-v1",
        "prefix_stripped": PREFIX,
        "pins_examined": len(pins),
        "pins_with_live_commit": len(pins) - len(dangling),
        "distinct_dangling_commits": len(by_commit),
        "resolved_count": len(mapping),
        "external_count": len(external),
        "unresolved_count": len(unresolved),
        "mapping": mapping,
        "external": external,
        "unresolved": unresolved,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="re-derive and fail if the committed artifact drifted")
    args = ap.parse_args()

    derived = build()
    text = json.dumps(derived, indent=1, sort_keys=True) + "\n"

    if args.check:
        if not ARTIFACT.exists():
            print("FAIL crosswalk artifact missing:", ARTIFACT)
            return 1
        if ARTIFACT.read_text(encoding="utf-8") != text:
            print("FAIL crosswalk artifact does not match a fresh derivation")
            return 1
        print(f"STANDALONE HISTORY CROSSWALK: PASS "
              f"({derived['resolved_count']} resolved, "
              f"{derived['external_count']} external, "
              f"{derived['unresolved_count']} unresolved)")
        return 0

    ARTIFACT.write_text(text, encoding="utf-8")
    print(f"wrote {ARTIFACT.relative_to(ROOT)}")
    print(f"  pins examined            : {derived['pins_examined']}")
    print(f"  distinct dangling commits: {derived['distinct_dangling_commits']}")
    print(f"  resolved                 : {derived['resolved_count']}")
    print(f"  external (tango/forge)   : {derived['external_count']}")
    print(f"  unresolved               : {derived['unresolved_count']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
