#!/usr/bin/env python3
"""Fail-closed activation gate for the separated scale/U(1) causal path."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PREDECESSOR = (
    ROOT
    / "d_quotient_classical/compensator/"
    "COMPENSATOR_COMPLEX_SCALE_U1_CONNECTION_PREFLIGHT_V1.json"
)
EXPECTED_SHA = "3b7b1f86392f0d5daeec4b1adac99a0e16e472ff37b44253908a20c53aad1404"
OUTPUT = (
    ROOT
    / "d_quotient_classical/compensator/"
    "COMPENSATOR_COMPLEX_SCALE_U1_FULL_BV_CAUSAL_GATE_V1.json"
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build() -> dict[str, Any]:
    actual = _sha(PREDECESSOR)
    source = json.loads(PREDECESSOR.read_text())
    if (
        actual != EXPECTED_SHA
        or source["result_id"]
        != "COMPENSATOR_COMPLEX_SCALE_U1_CONNECTION_PREFLIGHT_V1"
        or source["result_state"]
        != "SCOPED_SEPARATED_SCALE_U1_MINIMAL_GOOD_LOCUS_EMPTY"
        or source["terminal_verdict"]["healthy_locus"] != "EMPTY"
        or source["terminal_verdict"]["selected_action"]
        or source["terminal_verdict"]["causal_completion_activated"]
    ):
        raise AssertionError("separated scale/U1 activation input drifted")

    skipped = {
        name: {
            "status": "NOT_ACTIVATED",
            "reason": (
                "The hash-pinned predecessor has empty healthy coefficient "
                "locus and exports no selected action."
            ),
        }
        for name in (
            "action_derived_full_BV_rows",
            "Q_squared_and_cyclicity",
            "cylinder_and_Berger_reduced_inertia",
            "principal_symbols_and_Jordan_structure",
            "retarded_advanced_causal_parent",
            "support_aware_Green_homotopies",
            "raw_D_scale_phase_and_Berger_charges",
            "dressed_trace_quartet_and_relational_clock",
            "nonlinear_q2",
            "quantum_regulator_import",
        )
    }
    verdict = {
        "result": "NOT_ACTIVATED_EMPTY_PREDECESSOR_LOCUS",
        "full_gate_activated": False,
        "selected_action": False,
        "causal_parent_constructed": False,
        "zero_charge_sector_declared": False,
        "nonlinear_or_quantum_successor_activated": False,
        "reason": (
            "Activation is forbidden because the predecessor proves an empty "
            "minimal healthy locus by both scale-Ward and compact-Gauss "
            "separators."
        ),
    }
    claim_boundary = (
        "This is a conditional-gate closure, not a new causal no-go. It "
        "imports the exact terminal separated scale/U1 preflight and records "
        "that no action-derived BV carrier, Green homotopy, pairing, charge "
        "sector, nonlinear q2 or quantum import was constructed. It preserves "
        "the predecessor's scope and does not exclude charged sources, extra "
        "moduli, other boundaries, backgrounds or representations."
    )
    payload = {
        "schema": "pure-weyl-compensator-complex-scale-u1-full-bv-causal-gate-v1",
        "result_id": "COMPENSATOR_COMPLEX_SCALE_U1_FULL_BV_CAUSAL_GATE_V1",
        "result_state": "NOT_ACTIVATED_EMPTY_PREDECESSOR_LOCUS",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "predecessor": {
            "path": str(PREDECESSOR.relative_to(ROOT)),
            "sha256": actual,
            "source_commit": "6cc041fadaaf6259142aa8f30a2f75879cf92dd3",
            "result_id": source["result_id"],
            "result_state": source["result_state"],
            "healthy_locus": source["terminal_verdict"]["healthy_locus"],
            "selected_action": source["terminal_verdict"]["selected_action"],
        },
        "activation_condition": (
            "predecessor healthy_locus NONEMPTY and selected_action true"
        ),
        "activation_condition_satisfied": False,
        "skipped_gates": skipped,
        "terminal_verdict": verdict,
        "claim_flags": {
            "BV_COMPLETION": False,
            "CAUSAL_PARENT": False,
            "GREEN_HOMOTOPY": False,
            "PAIRING_OR_CHARGE_PASS": False,
            "NONLINEAR_Q2": False,
            "QUANTUM_IMPORT": False,
        },
        "claim_boundary": claim_boundary,
    }
    payload["content_hashes"] = {
        "predecessor_sha256": _digest(payload["predecessor"]),
        "skipped_gates_sha256": _digest(skipped),
        "verdict_sha256": _digest(verdict),
        "claim_boundary_sha256": _digest(claim_boundary),
    }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != rendered:
            raise SystemExit("generated conditional full-gate closure drifted")
        print(f"{payload['result_id']}: PASS")
        return
    OUTPUT.write_text(rendered)
    print(OUTPUT)


if __name__ == "__main__":
    main()
