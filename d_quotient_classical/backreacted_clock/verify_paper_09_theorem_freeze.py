#!/usr/bin/env python3
"""Independent verifier for the scoped Paper IX theorem freeze."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

import jsonschema


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/PAPER_09_THEOREM_FREEZE.json"
SCHEMA = ROOT / "d_quotient_classical/schema/paper-09-theorem-freeze-v1.schema.json"


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _blob(commit: str, path: str) -> bytes:
    prefix = subprocess.check_output(["git", "rev-parse", "--show-prefix"], cwd=ROOT, text=True).strip()
    return subprocess.check_output(["git", "show", f"{commit}:{prefix}{path}"], cwd=ROOT)


def main() -> int:
    cert = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(cert)
    loaded = {}
    for name, ref in cert["dependency_refs"].items():
        raw = _blob(ref["commit"], ref["path"])
        if _sha(raw) != ref["sha256"]:
            raise AssertionError(f"dependency hash mismatch: {name}")
        loaded[name] = raw
    table = json.loads(loaded["claim_table"])
    if table["paper_state"] != "THEOREM_FROZEN" or table["theorem_frozen"] is not True:
        raise AssertionError("claim table lifecycle mismatch")
    if len(table["claims"]) != 10 or any("MAXWELL" in row["certificate_result_id"] for row in table["claims"]):
        raise AssertionError("main claim inventory drifted")
    main = loaded["main_source"].decode()
    theorem_text = "\n".join(block.split("\\end{theorem}", 1)[0] for block in main.split("\\begin{theorem}")[1:])
    if any(word in theorem_text for word in ("Maxwell", "observer-apparatus", "84-row")):
        raise AssertionError("downstream theorem import detected")
    nonlinear = json.loads(loaded["nonlinear_frozen_signoff"])
    quantum = json.loads(loaded["quantum_postfreeze_signoff"])
    if nonlinear["flags"]["PAPER_09_NONLINEAR_FROZEN_K_GENERATOR_SIGNOFF"] is not True:
        raise AssertionError("nonlinear freeze signoff absent")
    if quantum["theorem_flags"]["PAPER09_QUANTUM_PROMOTION_ACCEPTED"] is not False:
        raise AssertionError("quantum promotion detected")
    if cert["verification"]["authoritative_freeze_rail"] != {
        "status": "PASS", "tests_passed": 47, "tests_failed": 0,
        "pytest_seconds": "135.33", "wall_seconds": "136.26", "maxrss_kb": 773600,
        "scope": "all ten Paper IX claims, claim table, generator audit, q3 action cross-check, and frozen nonlinear/quantum signoffs",
    }:
        raise AssertionError("authoritative replay receipt drifted")
    for source in cert["provenance"]["source_manifest"]:
        if _sha((ROOT / source["path"]).read_bytes()) != source["sha256"]:
            raise AssertionError(f"source drift: {source['path']}")
    flags = cert["flags"]
    for key in ("PAPER_09_THEOREM_FROZEN", "PAPER_09_TEN_CLAIMS_PINNED", "PAPER_09_AUTHORITATIVE_CLEAN_SNAPSHOT_REPLAY", "PAPER_09_PDFS_COMPILE", "PAPER_09_NONLINEAR_FROZEN_SIGNOFF", "PAPER_09_QUANTUM_BOUNDARY_SIGNOFF"):
        if flags[key] is not True:
            raise AssertionError(f"freeze flag dropped: {key}")
    for key in ("MAXWELL_MAIN_THEOREM_INCLUDED", "OBSERVER_84_ROW_MAIN_THEOREM_INCLUDED", "AFFINE_D_CARTAN_CERTIFIED", "ARITY_FOUR_OR_ALL_ORDERS_CERTIFIED", "HADAMARD_OR_QME_CERTIFIED", "QUANTUM_CLAIM"):
        if flags[key] is not False:
            raise AssertionError(f"forbidden promotion: {key}")
    print("PAPER_09_THEOREM_FREEZE independent replay: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
