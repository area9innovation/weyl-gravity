#!/usr/bin/env python3
"""Exact DR/MS evanescent-closure obstruction for the tau-adic QAP."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPO = ROOT.parents[1]
SOURCE_COMMIT = "7fabe9878"
HISTORICAL = {
    "certificate": {
        "path": (
            "quantum-weyl/anomalies/certificates/"
            "TAU_ADIC_ALL_LOOP_LOCAL_QME_STABILITY.json"
        ),
        "sha256": "a0ce9774fc1417d4e108a6b834173bc41fd433ed45bfcfdcf2d63063969f33bc",
    },
    "manuscript": {
        "path": "paper/12-pure-weyl-one-loop-bv-anomaly.tex",
        "sha256": "d2cedfb85a8bf7b1bc5ef2c606c186bdf253767fff30188858cedc0c1982fc1f",
    },
}


def _historical(path: str) -> bytes:
    return subprocess.run(
        [
            "git",
            "show",
            f"{SOURCE_COMMIT}:physics/symplectic-reconstruction/{path}",
        ],
        cwd=REPO,
        check=True,
        capture_output=True,
    ).stdout


def build() -> dict[str, Any]:
    for name, pin in HISTORICAL.items():
        if hashlib.sha256(_historical(pin["path"])).hexdigest() != pin["sha256"]:
            raise ValueError(f"historical QAP input drifted: {name}")

    # Two admissible dimensional continuations can differ by epsilon X_ev:
    # E_d^(X) = E_d^(0) + epsilon X_ev. The nonzero Euler pole a/epsilon
    # therefore makes their finite parts differ by a X_ev. The certified
    # four-dimensional algebra contains neither X_ev nor its mixing map.
    a = Fraction(-87, 20)
    continuation = [Fraction(1), Fraction(1)]  # coefficients of E4, eps X_ev
    pole_residue = [a * entry for entry in continuation]
    finite_evanescent = pole_residue[1]
    if finite_evanescent == 0:
        raise ValueError("Euler evanescent carrier unexpectedly vanished")

    value = {
        "schema": "quantum-weyl-tau-adic-dr-ms-qap-obstruction-v1",
        "result_id": "TAU_ADIC_DR_MS_QAP_EVANESCENT_CLOSURE_OBSTRUCTION",
        "result_state": "DECLARED_DR_MS_ARCHITECTURE_OBSTRUCTED_AT_EVANESCENT_CLOSURE",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "historical_input_pins": {
            key: {**pin, "source_commit": SOURCE_COMMIT}
            for key, pin in HISTORICAL.items()
        },
        "declared_architecture": {
            "regularization": "dimensional_regularization_d=4-epsilon",
            "subtraction": "minimal_subtraction_with_local_BV_antifield_insertions",
            "variables": "dressed g_hat plus complete minimal/nonminimal BV complex",
            "measure": "continued gauge-fixed Berezin measure with primed zero modes",
            "tau_topology": "formal tau-adic coefficientwise continuation",
            "power_counting": "massless logarithmic operators of dimension four",
            "coupling_chart": "formal neighbourhood of nonzero C2 kinetic coupling",
            "zero_modes": "project before determinant, retain local UV pole separately",
        },
        "first_incompatibility": {
            "gate": "COUNTERTERM_ALGEBRA_CLOSED_UNDER_SUBTRACTION",
            "four_dimensional_module": [
                "C(g_hat)^2",
                "E4(g_hat)",
                "R(g_hat)^2",
                "C(g_hat) dual C(g_hat)",
            ],
            "dimensional_continuation_ambiguity": (
                "E_d^(X)=E_d^(0)+epsilon X_ev+O(epsilon^2)"
            ),
            "nonzero_Euler_residue": {"numerator": -87, "denominator": 20},
            "pole_times_evanescent_identity": (
                "(a/epsilon)(E_d^(X)-E_d^(0))=a X_ev+O(epsilon)"
            ),
            "finite_evanescent_coefficient": {
                "numerator": finite_evanescent.numerator,
                "denominator": finite_evanescent.denominator,
            },
            "continuation_dependence": (
                "finite_MS(E_d^(X))-finite_MS(E_d^(0))=a X_ev != 0"
            ),
            "status": "EXACT_EVANESCENT_CONTINUATION_DEPENDENCE",
        },
        "qap_hypothesis_ledger": [
            {"hypothesis": "local first breaking", "status": "NOT_REACHED"},
            {"hypothesis": "ghost number one", "status": "NOT_REACHED"},
            {"hypothesis": "homogeneous dimension four", "status": "NOT_REACHED"},
            {"hypothesis": "Wess-Zumino consistency", "status": "NOT_REACHED"},
            {
                "hypothesis": "subtraction continuous and closed in declared algebra",
                "status": "FAILED_EVANESCENT_EXTENSION_REQUIRED",
            },
            {"hypothesis": "regular Koszul-Tate chart", "status": "NOT_REACHED"},
        ],
        "missing_completion": [
            "d-dimensional BV master action and differential",
            "complete evanescent ghost-zero and ghost-one operator basis",
            "mixing matrix from evanescent to physical operators",
            "nonminimal measure and antifield insertion continuation",
            "projection/finite-renormalization prescription after subdivergence subtraction",
            "independent QAP proof on the enlarged algebra",
        ],
        "receiver_status": "REJECT_UNCONDITIONAL_ALL_LOOP_PROMOTION",
        "claim_flags": {
            "ALL_REGULATORS_OBSTRUCTED": False,
            "UNCONDITIONAL_ALL_LOOP_QME": False,
            "DR_MS_QAP_CERTIFIED": False,
            "STRICT_THEORY_REPAIRED": False,
            "LORENTZIAN_QME_CERTIFIED": False,
        },
        "next_gate": (
            "Enlarge the formal algebra to a content-addressed d-dimensional "
            "evanescent BV module and prove its subtraction/mixing/projection "
            "maps, or construct a distinct four-dimensional regulator with "
            "an independent QAP proof."
        ),
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC/EUCLIDEAN-SPECTRAL result obstructs "
            "only the declared dimensional-regularization/minimal-subtraction "
            "architecture when it is required to stay inside the certified "
            "strictly four-dimensional tau-adic H04 module. The nonzero Euler "
            "pole turns an admissible epsilon-times-evanescent continuation "
            "ambiguity into a finite carrier outside that module. It is not a "
            "no-go theorem for dimensional regularization after a complete "
            "evanescent BV extension, and is not a no-go theorem for all regulators, "
            "does not refute the conditional cohomological induction, and does "
            "not establish convergence, global anomaly freedom, a Lorentzian "
            "QME, residual transfer, states, particles or unitarity."
        ),
    }
    validate(value)
    return value


def validate(value: dict[str, Any]) -> None:
    failed = [
        row for row in value["qap_hypothesis_ledger"]
        if row["status"].startswith("FAILED")
    ]
    if (
        value["result_state"]
        != "DECLARED_DR_MS_ARCHITECTURE_OBSTRUCTED_AT_EVANESCENT_CLOSURE"
        or value["first_incompatibility"]["status"]
        != "EXACT_EVANESCENT_CONTINUATION_DEPENDENCE"
        or value["first_incompatibility"]["finite_evanescent_coefficient"]
        != {"numerator": -87, "denominator": 20}
        or len(failed) != 1
        or failed[0]["hypothesis"]
        != "subtraction continuous and closed in declared algebra"
        or value["receiver_status"]
        != "REJECT_UNCONDITIONAL_ALL_LOOP_PROMOTION"
        or any(value["claim_flags"].values())
    ):
        raise ValueError("DR/MS evanescent obstruction boundary crossed")


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))
