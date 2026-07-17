#!/usr/bin/env python3
"""Independent replay of the retained observer K-descent typing gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
SCHEMA = PACKAGE / "schema/berger-retained-observer-k-descent-gate-v1.schema.json"
CERTIFICATE = PACKAGE / "certificates/BERGER_RETAINED_OBSERVER_K_DESCENT_GATE.json"


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _prefix() -> str:
    return subprocess.check_output(["git", "rev-parse", "--show-prefix"], cwd=ROOT, text=True).strip()


def main() -> int:
    certificate = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(certificate)
    for source in certificate["provenance"]["source_manifest"]:
        raw = (ROOT / source["path"]).read_bytes()
        if _sha(raw) != source["sha256"]:
            raise AssertionError(f"source drift: {source['path']}")
    dependencies = {}
    for name, ref in certificate["dependency_refs"].items():
        raw = subprocess.check_output(
            ["git", "show", f"{ref['snapshot_commit']}:{_prefix()}{ref['path']}"], cwd=ROOT
        )
        payload = json.loads(raw)
        if _sha(raw) != ref["sha256"] or payload["result_id"] != ref["result_id"]:
            raise AssertionError(f"dependency mismatch: {name}")
        if any(payload.get("flags", {}).get(flag) is not True for flag in ref["required_flags"]):
            raise AssertionError(f"dependency flag mismatch: {name}")
        dependencies[name] = payload
    retained = dependencies["retained_36_sdr"]["retained_complex"]["component_rows"]
    retained_ids = {row["row_id"] for row in retained}
    allocation = dependencies["global_rods"]["allocation_correction"]
    apparatus_ids = set(allocation["new_degree_zero_rows"] + allocation["new_degree_one_rows"])
    if len(retained) != 36 or retained_ids & apparatus_ids:
        raise AssertionError("retained36 unexpectedly types an apparatus row")
    if len(apparatus_ids) != 20 or allocation["corrected_proposed_total_rows"] != 84:
        raise AssertionError("84-row allocation mismatch")

    nu = sp.sqrt(58) / 6
    delta = sp.Rational(1, 96)
    for phase in (sp.sqrt(10) / 12, sp.sqrt(10) / 6):
        value = -nu * (3 * sp.sqrt(10) * sp.cos(phase) / 10) * sp.sin(nu * delta)
        if sp.simplify(value) == 0 or not delta < sp.Rational(1, 48):
            raise AssertionError("nonzero in-window K-rod witness failed")
    flags = certificate["flags"]
    for key in ("PROBE_RANK_TWO_BASELINE", "K_ROD_VARIATION_NONZERO_ON_DETECTOR_WINDOWS", "RETAINED36_APPARATUS_ROWS_ABSENT", "APPARATUS_84_ROW_COMPLEX_REQUIRED"):
        if flags[key] is not True:
            raise AssertionError(f"positive gate flag dropped: {key}")
    for key in ("RETAINED36_OBSERVER_VERTEX_TYPED", "RETAINED36_K_DESCENT_CERTIFIED", "APPARATUS_84_ROW_COMPLEX_CERTIFIED", "APPARATUS_84_ROW_CAUSAL_GREEN_HOMOTOPY_CERTIFIED", "CLASSICAL_OBSERVER_MAP_CERTIFIED", "GLOBAL_OBSERVER_PROGRAMME_NO_GO", "QUANTUM_CLAIM"):
        if flags[key] is not False:
            raise AssertionError(f"illegal promotion: {key}")
    print("BERGER_RETAINED_OBSERVER_K_DESCENT_GATE independent replay: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
