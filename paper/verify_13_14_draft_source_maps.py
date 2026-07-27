#!/usr/bin/env python3
"""Fail-closed source pinning for the Paper 13 and Paper 14 working drafts.

The historical monorepo baseline commit may not have a standalone commit
image.  The source maps also pin every input by Git blob id, so the
standalone verifier authenticates each declared path/blob pair directly
against the filtered history without rewriting the historical baseline.
"""

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


def _blob_seen_at_path(path: str, blob: str) -> bool:
    try:
        object_type = _git("cat-file", "-t", blob)
    except subprocess.CalledProcessError:
        return False
    if object_type != "blob":
        return False
    commits = _git("log", "--all", "--format=%H", "--", path).splitlines()
    for commit in commits:
        try:
            if _git("rev-parse", f"{commit}:{path}") == blob:
                return True
        except subprocess.CalledProcessError:
            continue
    return False


def verify_map(map_path: Path) -> tuple[str, int]:
    payload = json.loads(map_path.read_text(encoding="utf-8"))
    assert payload["schema"] == "paper-draft-source-map-v1"
    if payload["paper_id"] == "PAPER_13_COMPACT_WEYL_MAXWELL_SECOND_ORDER_TANGENT_CONE":
        assert payload["lifecycle_state"] == "THEOREM_FROZEN"
        assert payload["structural_theorem_lifecycle_state"] == "THEOREM_FROZEN"
        assert payload["bounded_common_zero_lifecycle_state"] == "OPEN"
    else:
        assert payload["lifecycle_state"] == "DRAFT_ALLOWED"

    baseline = payload["source_baseline"]
    assert len(baseline) == 40 and all(c in "0123456789abcdef" for c in baseline)

    manuscript = ROOT / payload["manuscript"]
    assert manuscript.exists(), manuscript
    assert manuscript.with_suffix(".pdf").exists(), manuscript.with_suffix(".pdf")

    seen: set[str] = set()
    for source in payload["sources"]:
        path = source["path"]
        assert path not in seen
        seen.add(path)
        assert _blob_seen_at_path(path, source["git_blob"]), (
            path,
            source["git_blob"],
            "pinned blob absent from declared path history",
        )

    assert payload["next_gate"]
    return payload["paper_id"], len(seen)


def main() -> None:
    for map_path in MAPS:
        paper_id, count = verify_map(map_path)
        print(f"PASS {paper_id}: {count} content-pinned inputs authenticated")


if __name__ == "__main__":
    main()
