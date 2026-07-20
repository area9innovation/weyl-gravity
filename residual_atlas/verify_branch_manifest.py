#!/usr/bin/env python3
"""Independent committed-snapshot verifier for the residual branch manifest."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PREFIX = "physics/symplectic-reconstruction/"
MANIFEST = ROOT / "residual_atlas/residual-branch-manifest-v1.json"
SCHEMA = ROOT / "residual_atlas/schema/residual-branch-manifest-v1.schema.json"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _get(value: Any, path: str) -> Any:
    for part in path.split("."):
        value = value[part]
    return value


def verify(manifest_path: Path = MANIFEST) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(manifest)
    commit = manifest["source_snapshot_commit"]
    fragments: dict[str, dict[str, Any]] = {}
    inventory: list[str] = []
    for record in manifest["fragments"]:
        raw = subprocess.check_output(["git", "show", f"{commit}:{PREFIX}{record['path']}"], cwd=REPO)
        assert _sha256(raw) == record["sha256"]
        payload = json.loads(raw)
        ids = [entry["id"] for entry in payload["entries"]]
        assert len(ids) == record["entry_count"]
        assert ids == record["entry_ids"]
        assert _sha256(("\n".join(ids) + "\n").encode()) == record["entry_ids_sha256"]
        fragments[record["key"]] = {entry["id"]: entry for entry in payload["entries"]}
        inventory.extend(f"{record['key']}:{entry_id}" for entry_id in ids)
    assert _sha256(("\n".join(inventory) + "\n").encode()) == manifest["coverage"]["row_inventory_sha256"]
    assert len(inventory) == manifest["coverage"]["total_source_rows"]

    branch_ids = {branch["id"] for branch in manifest["branches"]}
    assert len(branch_ids) == len(manifest["branches"])
    for branch in manifest["branches"]:
        assert set(branch["cells"]) == set(manifest["cell_axes"])
        for source_row in branch["source_rows"]:
            assert source_row["entry_id"] in fragments[source_row["fragment"]]
        for cell in branch["cells"].values():
            for source in cell["sources"]:
                entry = fragments[source["fragment"]][source["entry_id"]]
                value = _get(entry, source["field_path"])
                if isinstance(value, dict):
                    assert value["status"] == source["observed_status"]
                    assert value["statement"] == source["observed_statement"]
                else:
                    assert value == source["observed_status"]

    for crosswalk in manifest["crosswalks"]:
        assert set(crosswalk["from_branches"]) <= branch_ids
        assert set(crosswalk["to_branches"]) <= branch_ids
        source = crosswalk["source"]
        value = _get(fragments[source["fragment"]][source["entry_id"]], source["field_path"])
        assert value["status"] == crosswalk["status"] == source["observed_status"]
        assert value["statement"] == crosswalk["statement"] == source["observed_statement"]

    no_map_ids = {
        "crosswalk.ph_to_vacuum_cylinder",
        "crosswalk.ph_to_black_hole",
        "crosswalk.ph_exceptional_to_berger_observer",
        "crosswalk.berger_branch_to_detector",
    }
    by_crosswalk = {row["id"]: row for row in manifest["crosswalks"]}
    assert all(by_crosswalk[row_id]["status"] == "NO_CERTIFIED_MAP" for row_id in no_map_ids)
    assert by_crosswalk["crosswalk.berger_unsplit_to_ph_branches"]["status"] == "OBSTRUCTED"


if __name__ == "__main__":
    verify()
    print("RESIDUAL_BRANCH_MANIFEST_V1 independent verification: PASS")
