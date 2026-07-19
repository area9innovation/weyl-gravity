"""Register the fail-closed relative quantum readiness row in the D dossier."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROGRAMME = ROOT / "d_quotient_programme"
OUTPUT = PROGRAMME / "contributions/quantum-relative-einstein-weyl-readiness.json"
SCHEMA = PROGRAMME / "schema/team-contribution-v1.schema.json"
PHASES = PROGRAMME / "registry/phase_spaces.json"
EVIDENCE_COMMIT = "a0132ed1f71e28f0473aa93a86aed2bf9919c282"
EVIDENCE_PATH = "quantum-weyl/relative/certificates/QUANTUM_RELATIVE_EINSTEIN_WEYL_QME_DEFECT_READINESS.json"
WORKING_EVIDENCE = ROOT / EVIDENCE_PATH


def _evidence_bytes() -> bytes:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "show", f"{EVIDENCE_COMMIT}:./{EVIDENCE_PATH}"]
    )


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _phase_space() -> dict[str, Any]:
    rows = json.loads(PHASES.read_text())["phase_spaces"]
    matches = [
        row for row in rows
        if row["phase_space_id"]
        == "einstein_maxwell_product_compact_weyl_complete_standard_harmonic_tangent"
    ]
    if len(matches) != 1:
        raise ValueError("relative quantum phase space is not uniquely registered")
    return matches[0]


def build_contribution() -> dict[str, Any]:
    evidence_bytes = _evidence_bytes()
    evidence = json.loads(evidence_bytes)
    if WORKING_EVIDENCE.read_bytes() != evidence_bytes:
        raise ValueError("working relative readiness certificate differs from pinned commit")
    if (
        evidence.get("result_state")
        != "LINEAR_RELATIVE_TRIANGLE_AND_OBSERVABLE_PULLBACK_IMPORTED_NONLINEAR_QME_OPEN"
        or evidence.get("verdict") != "ANALYTIC_FRAMEWORK_MISSING"
        or evidence.get("shared_relative_row", {}).get("map_iota")
        != "COMPLETE_ALL_ROW_SUPPORT_LOCAL_NONCYCLIC_LINEAR_TRIANGLE_IMPORTED"
        or evidence.get("claim_flags", {}).get("RELATIVE_OBSERVABLE_PULLBACK_IMPORTED")
        is not True
        or evidence.get("claim_flags", {}).get("RELATIVE_EQUIVARIANCE_IMPORTED")
        is not True
        or evidence.get("qme_and_transfer_gate", {}).get("residual_quantum_transfer_authorized")
        is not False
    ):
        raise ValueError("relative readiness evidence crossed its fail-closed boundary")
    phase = _phase_space()
    return {
        "schema": "pure-weyl-d-quotient-team-contribution-v1",
        "team_id": "quantum",
        "setting_id": "compact_einstein_maxwell_weyl_relative_quantum_readiness",
        "generator_id": "D_compact",
        "phase_space_id": phase["phase_space_id"],
        "boundary_conditions": phase["boundary_conditions"],
        "lifecycle_layer": "QUANTUM",
        "claim_status": "BLOCKED",
        "verdict": "ANALYTIC_FRAMEWORK_MISSING",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "established": [
            "G1 complete linear relative import on the compact Einstein-Maxwell product background",
            "content-hash import of the certified on-shell standard-harmonic inclusion and classical reduced-mode pullback pairing",
            "content-hash import of the all-row support-local noncyclic off-shell linear triangle and exact mapping cofiber",
            "contravariant support-local pullback on the linear local BRST observable DGA with exact H_product equivariance",
            "exact reduced-mode coefficient detectors for every certified extra cofiber, explicitly not promoted to spacetime or quantum observables",
            "content-hash import of a partial quadratic relative preflight without promotion to a complete O2 or arity-three theorem",
            "formal relative anomaly subtraction target with bulk, antifield, boundary, zero-mode, measure, central and D-Cartan ledgers separated",
            "fail-closed nonlinear, local QME, state, pairing and residual-transfer statuses",
        ],
        "not_established": [
            "a standard-pairing cyclic relative map or renormalized relative pairing",
            "the complete relative f2 or arity-three Linfinity disposition",
            "the final relative residual quotient or renormalized observable pullback",
            "Einstein or Weyl QME restoration and a defined relative anomaly class",
            "a renormalized relative pairing, BRST-compatible state restriction or quantum D-Cartan verdict",
            "a particle, Hilbert-space, unitarity or Lorentzian quantum theorem",
        ],
        "evidence": {
            "path": EVIDENCE_PATH,
            "commit": EVIDENCE_COMMIT,
            "sha256": _sha256(evidence_bytes),
        },
        "verification_commands": [
            "PYTHONPATH=quantum-weyl python3 -m relative.einstein_weyl_qme_readiness_certificate --check",
            "PYTHONPATH=quantum-weyl python3 -m relative.verify_einstein_weyl_qme_readiness",
            "PYTHONPATH=quantum-weyl python3 -m relative.contribution --check",
            "PYTHONPATH=quantum-weyl python3 -m unittest discover -s quantum-weyl/relative/tests -v",
        ],
        "next_gate": "import EINSTEIN_WEYL_RELATIVE_LINFINITY_THROUGH_ARITY_THREE, then compute matched Einstein and Weyl QME dispositions and a renormalized observable restriction while retaining ANALYTIC_FRAMEWORK_MISSING",
    }


def validate_contribution(record: object) -> None:
    if not isinstance(record, dict):
        raise ValueError("relative quantum contribution must be an object")
    schema = json.loads(SCHEMA.read_text())
    if set(record) != set(schema["required"]):
        raise ValueError("relative quantum contribution fields differ from schema")
    if (
        record.get("team_id") != "quantum"
        or record.get("lifecycle_layer") != "QUANTUM"
        or record.get("claim_status") != "BLOCKED"
        or record.get("verdict") != "ANALYTIC_FRAMEWORK_MISSING"
        or record.get("dependency_tags")
        != ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"]
    ):
        raise ValueError("relative quantum contribution scope drifted")
    evidence = record.get("evidence", {})
    if (
        set(evidence) != {"path", "commit", "sha256"}
        or re.fullmatch(r"[0-9a-f]{40}", evidence["commit"]) is None
        or re.fullmatch(r"[0-9a-f]{64}", evidence["sha256"]) is None
    ):
        raise ValueError("relative quantum evidence record is malformed")
    content = subprocess.check_output(
        ["git", "-C", str(ROOT), "show", f"{evidence['commit']}:./{evidence['path']}"]
    )
    if _sha256(content) != evidence["sha256"]:
        raise ValueError("relative quantum evidence hash mismatch")


def _text(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    contribution = build_contribution()
    validate_contribution(contribution)
    content = _text(contribution)
    if args.emit:
        OUTPUT.write_text(content)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != content):
        raise SystemExit(f"stale relative quantum contribution: {OUTPUT}")
    print("QUANTUM RELATIVE CONTRIBUTION: BLOCKED, ANALYTIC FRAMEWORK MISSING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
