#!/usr/bin/env python3
"""Verify the fail-closed full prolonged Green-bridge dependency theorem."""

from __future__ import annotations

from copy import deepcopy
import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.prolonged_green_bridge import (
    ProlongedGreenBridge,
)


CERTIFICATES = ROOT / "covariant_completion" / "certificates"
SUBSTITUTION = CERTIFICATES / "curved_curvature_mapping_cylinder_substitution.json"
CURVATURE_WITNESS = CERTIFICATES / "curved_weyl_cotton_block_green_witness.json"
CAUSAL_PDE = CERTIFICATES / "curved_weyl_cotton_causal_pde.json"
RECOGNITION = CERTIFICATES / "green_operator_chain_compatibility.json"
OUTPUT = CERTIFICATES / "curved_prolonged_green_bridge.json"


def _load(path: Path) -> dict[str, object]:
    if not path.exists():
        raise AssertionError(f"required certificate is absent: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"certificate is not an object: {path.relative_to(ROOT)}")
    return value


def _rejects(
    substitution: dict[str, object],
    witness: dict[str, object],
    causal: dict[str, object],
    recognition: dict[str, object],
) -> bool:
    try:
        ProlongedGreenBridge(substitution, witness, causal, recognition).verify()
    except AssertionError:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    substitution = _load(SUBSTITUTION)
    witness = _load(CURVATURE_WITNESS)
    causal = _load(CAUSAL_PDE)
    recognition = _load(RECOGNITION)
    bridge = ProlongedGreenBridge(substitution, witness, causal, recognition)
    certificate = bridge.certificate()

    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", OUTPUT.relative_to(ROOT))

    checks = {
        "coefficientwise_Q_input": certificate["exact_inputs"][
            "coefficientwise_16_block_Q"
        ],
        "triangular_left_inverse": certificate[
            "finite_triangular_green_theorem"
        ]["left_inverse_defect"] == 0,
        "triangular_right_inverse": certificate[
            "finite_triangular_green_theorem"
        ]["right_inverse_defect"] == 0,
        "finite_causal_formula": certificate[
            "finite_triangular_green_theorem"
        ]["finite_no_Neumann_convergence_assumption"],
        "recognition_complete": certificate["recognition_after_full_witness"][
            "purely_formal_step_complete"
        ],
        "missing_W_visible": bool(
            certificate["single_missing_constructive_certificate"]["required_data"]
        ),
        "no_overpromotion": not certificate["prolonged_green_witness"]
        and not certificate["curvature_causal_green_operators"]
        and not certificate["causal_green_homotopy"],
    }

    if args.guards:
        bad_substitution = deepcopy(substitution)
        bad_substitution["coefficientwise_complete_prolonged_Q"] = False
        bad_witness = deepcopy(witness)
        bad_witness["exact_block_identities"]["P_equals_QW_plus_WQ"] = False
        bad_causal = deepcopy(causal)
        bad_causal["curvature_block_causal_solution_operators"] = False
        bad_recognition = deepcopy(recognition)
        bad_recognition["green_homotopies"]["identity"] = "unproved"
        checks.update(
            {
                "incomplete_Q_rejected": _rejects(
                    bad_substitution, witness, causal, recognition
                ),
                "broken_kernel_witness_rejected": _rejects(
                    substitution, bad_witness, causal, recognition
                ),
                "missing_causal_PDE_rejected": _rejects(
                    substitution, witness, bad_causal, recognition
                ),
                "broken_recognition_rejected": _rejects(
                    substitution, witness, causal, bad_recognition
                ),
            }
        )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(
        "PROLONGED GREEN BRIDGE GUARDS: "
        f"{sum(checks.values())}/{len(checks)} PASS"
    )
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
