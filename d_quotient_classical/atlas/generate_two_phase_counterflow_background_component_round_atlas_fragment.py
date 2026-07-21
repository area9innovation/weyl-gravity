#!/usr/bin/env python3
"""Generate the schema-conforming counterflow component atlas fragment."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_BACKGROUND_COMPONENT_ROUND_DISPOSITION_V1.json"
OUTPUT = ROOT / "residual_atlas/two-phase-counterflow-background-component-round-fragment-v1.json"
GENERATOR = ROOT / "d_quotient_classical/atlas/generate_two_phase_counterflow_background_component_round_atlas_fragment.py"
ALLOWED = ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _claim(status: str, statement: str) -> dict[str, str]:
    if status not in ALLOWED:
        raise AssertionError("invalid atlas status")
    return {"status": status, "statement": statement}


def _second_order(causal_status: str, causal_statement: str) -> dict[str, Any]:
    return {
        "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
        "bounded_or_finite_quasiperiodic": _claim("NO_CERTIFIED_MAP", "No selected-action q2 correction is imported."),
        "smooth_secular": _claim("NO_CERTIFIED_MAP", "No selected-action secular correction is imported."),
        "causal_retarded": _claim(causal_status, causal_statement),
    }


def build() -> dict[str, Any]:
    source = json.loads(SOURCE.read_text())
    if source["result_state"] != "CERTIFIED_ISOLATED_PHYSICAL_BERGER_COMPONENT_AND_ROUND_NONINHERITANCE":
        raise AssertionError("component theorem is not certified")
    evidence = [{"path": str(SOURCE.relative_to(ROOT)), "result_id": source["result_id"], "sha256": _sha(SOURCE)}]
    theory = "selected two-phase counterflow action with auxiliary diagonal U1 and separate Weyl scale quartet"
    entries = [
        {
            "id": "classical.two_phase_counterflow_component.selected_berger",
            "scope": {
                "theory": theory,
                "background": "stationary Berger R x S3, a=1, c_squared=9/40",
                "boundaries": "none; closed S3 Cauchy slices",
                "charge_sector": "unrestricted Q_rel plus explicit fixed-Q_rel leaf",
                "carrier": "complete real cyclic 70-component gauge-fixed BV carrier",
                "degree": 0,
                "parity": "full BV carrier; no round-cylinder parity crosswalk",
                "ell": "all certified Berger S3 Hodge sectors",
                "m": "all certified Berger carrier labels",
                "k": "NOT_APPLICABLE",
                "omega": "background Omega=3/4; perturbation frequencies carrier-dependent",
            },
            "descriptions": {"causal": "CERTIFIED", "symplectic": "CERTIFIED", "nonlinear": "OPEN", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            "mode_data": {
                "dispersion": _claim("CERTIFIED", "The constrained homogeneous trace roots are simple with lambda_squared=-659/240; the full unary carrier remains hash-imported."),
                "lee_wald": _claim("CERTIFIED", "The imported 70-component parent supplies the real cyclic pairing and relative-clock current."),
                "taub_maps": _claim("NO_CERTIFIED_MAP", "No selected-action q2 tangent-cone map is imported."),
                "resonance": _claim("NO_CERTIFIED_MAP", "No nonlinear resonance computation is imported."),
                "second_order": _second_order("OPEN", "The unary retarded carrier is certified, but its nonlinear source and q2 are not."),
            },
            "evidence": evidence,
            "claim_boundary": "The selected point is causal and symplectic, but its fixed-action stationary geometry component is a singleton. No neighbouring causal transport, q2, observer, quantum or round-mode identification is certified.",
        },
        {
            "id": "classical.two_phase_counterflow_component.same_action_round",
            "scope": {
                "theory": theory,
                "background": "round q=1 cylinder candidate under the same fixed action",
                "boundaries": "none; closed S3 Cauchy slices",
                "charge_sector": "candidate positive relative-charge sector",
                "carrier": "NO_CERTIFIED_MAP",
                "degree": 0,
                "parity": "NO_CERTIFIED_MAP",
                "ell": "NO_CERTIFIED_MAP",
                "m": "NO_CERTIFIED_MAP",
                "k": "NOT_APPLICABLE",
                "omega": "NO_CERTIFIED_MAP",
            },
            "descriptions": {"causal": "NO_CERTIFIED_MAP", "symplectic": "NO_CERTIFIED_MAP", "nonlinear": "OBSTRUCTED", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
            "mode_data": {
                "dispersion": _claim("OBSTRUCTED", "The same fixed action has no positive stationary q=1 solution; the formal branch has x=-119/160."),
                "lee_wald": _claim("NO_CERTIFIED_MAP", "No same-action positive round carrier exists on which to transport the pairing."),
                "taub_maps": _claim("NO_CERTIFIED_MAP", "No same-action round q2 map exists."),
                "resonance": _claim("NO_CERTIFIED_MAP", "The imported retuned round real-root obstruction is not a same-action mode crosswalk."),
                "second_order": _second_order("NO_CERTIFIED_MAP", "No same-action round unary carrier exists for a causal-retarded q2 problem."),
            },
            "evidence": evidence,
            "claim_boundary": "Negative crosswalk only: the selected fixed action does not reach a positive stationary round cylinder. The separately retuned round trace obstruction is imported as a boundary datum, not identified mode-by-mode.",
        },
    ]
    return {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "classical",
        "generated_by": str(GENERATOR.relative_to(ROOT)),
        "generated_by_sha256": _sha(GENERATOR),
        "status_vocabulary": ALLOWED,
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": entries,
        "verification_commands": [
            "python3 d_quotient_classical/compensator/two_phase_counterflow_background_component_round_disposition.py --check",
            "python3 d_quotient_classical/compensator/verify_two_phase_counterflow_background_component_round_disposition.py",
            "python3 d_quotient_classical/atlas/generate_two_phase_counterflow_background_component_round_atlas_fragment.py --check",
            "python3 residual_atlas/validate_fragment.py residual_atlas/two-phase-counterflow-background-component-round-fragment-v1.json",
        ],
    }


def write() -> None:
    OUTPUT.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")


def check() -> None:
    if json.loads(OUTPUT.read_text()) != build():
        raise AssertionError("stored atlas fragment drifted")
    print("TWO_PHASE_COUNTERFLOW_BACKGROUND_COMPONENT_ROUND_ATLAS_FRAGMENT_V1: PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    check() if args.check else write()


if __name__ == "__main__":
    main()
