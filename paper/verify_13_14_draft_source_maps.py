#!/usr/bin/env python3
"""Fail-closed source pinning for the Paper 13 and Paper 14 working drafts."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
MAPS = (
    ROOT / "paper/13-compact-weyl-maxwell-second-order-tangent-cone-claim-map.json",
    ROOT / "paper/14-pure-weyl-black-hole-radiation-claim-map.json",
)


def _git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=True, stderr=subprocess.STDOUT
    ).strip()


def main() -> None:
    repo = Path(_git("rev-parse", "--show-toplevel"))
    prefix = ROOT.relative_to(repo).as_posix()

    for map_path in MAPS:
        payload = json.loads(map_path.read_text(encoding="utf-8"))
        assert payload["schema"] == "paper-draft-source-map-v1"
        if payload["paper_id"] == "PAPER_13_COMPACT_WEYL_MAXWELL_SECOND_ORDER_TANGENT_CONE":
            assert payload["lifecycle_state"] == "THEOREM_FROZEN"
            assert payload["structural_theorem_lifecycle_state"] == "THEOREM_FROZEN"
            assert payload["bounded_common_zero_lifecycle_state"] == "OPEN"
        else:
            assert payload["lifecycle_state"] == "DRAFT_ALLOWED"
        baseline = payload["source_baseline"]
        assert _git("cat-file", "-t", baseline) == "commit"

        manuscript = ROOT / payload["manuscript"]
        assert manuscript.exists(), manuscript
        assert manuscript.with_suffix(".pdf").exists(), manuscript.with_suffix(".pdf")

        seen: set[str] = set()
        for source in payload["sources"]:
            path = source["path"]
            assert path not in seen
            seen.add(path)
            git_path = f"{prefix}/{path}" if prefix else path
            actual = _git("rev-parse", f"{baseline}:{git_path}")
            assert actual == source["git_blob"], (path, actual, source["git_blob"])

        assert payload["next_gate"]
        print(f"PASS {payload['paper_id']}: {len(seen)} committed inputs pinned")


if __name__ == "__main__":
    main()
