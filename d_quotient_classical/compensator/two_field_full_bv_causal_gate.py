#!/usr/bin/env python3
"""Fail-closed activation gate for the two-field compact-charge causal path."""

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
    "COMPENSATOR_TWO_FIELD_CHARGE_MATRIX_PREFLIGHT_V1.json"
)
EXPECTED_SHA = "e597c687ae064ac6809b674c056aa08d0167a9184b6addb95b5b7330c33dcc62"
OUTPUT = (
    ROOT
    / "d_quotient_classical/compensator/"
    "COMPENSATOR_TWO_FIELD_FULL_BV_CAUSAL_GATE_V1.json"
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
    terminal = source["terminal_verdict"]
    if (
        actual != EXPECTED_SHA
        or source["result_id"]
        != "COMPENSATOR_TWO_FIELD_CHARGE_MATRIX_PREFLIGHT_V1"
        or source["result_state"]
        != "SCOPED_TWO_FIELD_MINIMAL_CHARGE_MATRIX_GOOD_LOCUS_EMPTY"
        or terminal["healthy_locus"] != "EMPTY"
        or terminal["selected_action"]
        or terminal["full_BV_or_causal_completion_activated"]
    ):
        raise AssertionError("two-field activation input drifted")

    reason = (
        "The hash-pinned predecessor has an empty declared minimal healthy "
        "locus and exports no selected action or representation stratum."
    )
    skipped = {
        name: {"status": "NOT_ACTIVATED", "reason": reason}
        for name in (
            "selected_charge_stratum_and_action",
            "reducible_Diff_Weyl_compact_U1_BV_rows",
            "Q_squared_cyclicity_and_Noether_identities",
            "cylinder_and_Berger_constraint_reduction",
            "physical_scalar_vector_inertia",
            "characteristic_and_Jordan_data",
            "support_aware_retarded_advanced_Green_homotopies",
            "reduced_pairing",
            "raw_D_Berger_total_gauge_and_relative_phase_charges",
            "gauge_invariant_relational_phase_observable",
            "dressed_trace_elimination",
            "nonlinear_q2",
            "quantum_import",
        )
    }
    verdict = {
        "result": "NOT_ACTIVATED_EMPTY_PREDECESSOR_LOCUS",
        "full_gate_activated": False,
        "selected_action": False,
        "selected_charge_stratum": False,
        "causal_parent_constructed": False,
        "relative_clock_constructed": False,
        "nonlinear_or_quantum_successor_activated": False,
        "reason": (
            "The compact rank-one sector can preserve a neutral relative "
            "phase and pass the displayed Berger metric/Gauss fixture, but "
            "the predecessor proves that healthy scalar kinetic plus a "
            "physical clock makes the candidate scale reducible, while an "
            "independent phase-shifting scale gauges that clock."
        ),
    }
    claim_boundary = (
        "This is a conditional-gate closure, not a new causal no-go. It "
        "imports the exact terminal two-field charge-matrix preflight and "
        "records that no action-derived BV carrier, reduced pairing, Green "
        "homotopy, relational observable, nonlinear q2 or quantum import was "
        "constructed. It does not undo the positive compact-lattice result: "
        "primitive rank one leaves a neutral relative phase and the displayed "
        "Berger metric/Gauss fixture passes. The non-activation comes only "
        "from the predecessor's scoped scale/kinetic/clock trichotomy. "
        "Additional fields, non-Riemannian target constraints, higher "
        "derivatives, other backgrounds and representations remain open."
    )
    payload = {
        "schema": "pure-weyl-compensator-two-field-full-bv-causal-gate-v1",
        "result_id": "COMPENSATOR_TWO_FIELD_FULL_BV_CAUSAL_GATE_V1",
        "result_state": "NOT_ACTIVATED_EMPTY_PREDECESSOR_LOCUS",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "predecessor": {
            "path": str(PREDECESSOR.relative_to(ROOT)),
            "sha256": actual,
            "source_commit": "2b1609cedc77e85dd71967fb46e49a4595c75763",
            "result_id": source["result_id"],
            "result_state": source["result_state"],
            "healthy_locus": terminal["healthy_locus"],
            "selected_action": terminal["selected_action"],
            "full_BV_or_causal_completion_activated": terminal[
                "full_BV_or_causal_completion_activated"
            ],
            "compact_charge_lattice_result": terminal[
                "compact_charge_lattice_result"
            ],
            "first_obstruction": terminal["first_obstruction"],
        },
        "activation_condition": (
            "predecessor healthy_locus NONEMPTY, selected_action true, and "
            "full_BV_or_causal_completion_activated true"
        ),
        "activation_condition_satisfied": False,
        "skipped_gates": skipped,
        "terminal_verdict": verdict,
        "claim_flags": {
            "BV_COMPLETION": False,
            "CAUSAL_PARENT": False,
            "GREEN_HOMOTOPY": False,
            "REDUCED_PAIRING": False,
            "RELATIONAL_CLOCK_OBSERVABLE": False,
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
            raise SystemExit("generated two-field conditional gate drifted")
        print(f"{payload['result_id']}: PASS")
        return
    OUTPUT.write_text(rendered)
    print(OUTPUT)


if __name__ == "__main__":
    main()
