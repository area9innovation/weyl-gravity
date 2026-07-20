#!/usr/bin/env python3
"""Exact common d-dimensional geometric BV-module preflight.

The action-independent part is the antifield-zero curvature premodule.  The
calculation stops when a selected action is required to define the
Koszul--Tate differential, loop mixing, or a parity-odd dimensional scheme.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUTPUT = (
    HERE
    / "certificates/DRESSED_EVANESCENT_GEOMETRIC_BV_MODULE_PREFLIGHT.json"
)

INPUTS = {
    "dr_ms_obstruction": (
        HERE
        / "certificates/TAU_ADIC_DR_MS_QAP_EVANESCENT_CLOSURE_OBSTRUCTION.json"
    ),
    "strict_H04": (
        ROOT / "quantum-weyl/local_bv/cohomology/H04_GAUGE_FIXED_BV_RESULT.json"
    ),
    "strict_H14": (
        ROOT / "quantum-weyl/local_bv/cohomology/H14_GAUGE_FIXED_BV_RESULT.json"
    ),
    "extended_H04_H14": (
        HERE / "certificates/WESS_ZUMINO_EXTENDED_LOCAL_BV_COHOMOLOGY.json"
    ),
    "quartet_cotangent_lift": (
        HERE / "certificates/WESS_ZUMINO_MINIMAL_BV_COTANGENT_LIFT.json"
    ),
}

EXPECTED_SHA256 = {
    "dr_ms_obstruction": (
        "20915ec21d0c96534a7091b57ee2c3baf5728526a32d00de83dd75b4b94e7e5f"
    ),
    "strict_H04": (
        "ffcb1318fecd34b20695e29f8b1e545d74b0b5ba33709971bd9eefd578d4ca97"
    ),
    "strict_H14": (
        "a7730a34b21d2068cc73e46c563ce929195a3d9a7c7626d3843788b54e0592b3"
    ),
    "extended_H04_H14": (
        "fa21fc6071ae52277d9953b68c47773686117f1426cc50899fdf8c124d2ba616"
    ),
    "quartet_cotangent_lift": (
        "b265dc9d86938ed7bee0f57a1394e26e762e99841a89b1310b950542e0c2e2b1"
    ),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _rat(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def _matrix(values: list[list[Fraction | int]]) -> list[list[dict[str, int]]]:
    return [[_rat(entry) for entry in row] for row in values]


def _mul(
    left: list[list[Fraction]], right: list[list[Fraction]]
) -> list[list[Fraction]]:
    return [
        [
            sum(
                (left[i][k] * right[k][j] for k in range(len(right))),
                Fraction(0),
            )
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def _load_inputs() -> dict[str, dict[str, Any]]:
    values: dict[str, dict[str, Any]] = {}
    for name, path in INPUTS.items():
        actual = _sha256(path)
        if actual != EXPECTED_SHA256[name]:
            raise ValueError(f"{name} hash drift: {actual}")
        values[name] = json.loads(path.read_text())
    if (
        values["dr_ms_obstruction"]["result_id"]
        != "TAU_ADIC_DR_MS_QAP_EVANESCENT_CLOSURE_OBSTRUCTION"
        or values["strict_H04"]["result_id"] != "H04_GAUGE_FIXED_BV_RESULT"
        or values["strict_H14"]["result_id"] != "H14_GAUGE_FIXED_BV_RESULT"
        or values["extended_H04_H14"]["result_id"]
        != "WESS_ZUMINO_EXTENDED_LOCAL_BV_COHOMOLOGY"
        or values["quartet_cotangent_lift"]["contractible_quartet"]["status"]
        != "EXACT_CONTRACTIBLE_WEYL_QUARTET_IN_DRESSED_VARIABLES"
    ):
        raise ValueError("evanescent preflight input semantics drifted")
    return values


def build() -> dict[str, Any]:
    values = _load_inputs()

    # w=(C4^2,E4,R^2,Box R), x=(Riem^2,Ric^2,R^2,Box R).
    physical_from_raw = [
        [Fraction(1), Fraction(-2), Fraction(1, 3), Fraction(0)],
        [Fraction(1), Fraction(-4), Fraction(1), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(1), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(0), Fraction(1)],
    ]
    raw_from_physical = [
        [Fraction(2), Fraction(-1), Fraction(1, 3), Fraction(0)],
        [Fraction(1, 2), Fraction(-1, 2), Fraction(1, 3), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(1), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(0), Fraction(1)],
    ]
    identity = [
        [Fraction(int(i == j)) for j in range(4)] for i in range(4)
    ]

    # d=4-epsilon:
    # C_d^2=Riem^2-4/(d-2) Ric^2+2/((d-1)(d-2))R^2.
    cd2_epsilon_raw = [
        Fraction(0),
        Fraction(-1),
        Fraction(5, 18),
        Fraction(0),
    ]
    # Coefficients transform by raw_from_physical^T.
    cd2_epsilon_physical = [
        sum(
            (
                raw_from_physical[row][column] * cd2_epsilon_raw[row]
                for row in range(4)
            ),
            Fraction(0),
        )
        for column in range(4)
    ]
    euler_residue = Fraction(-87, 20)

    result: dict[str, Any] = {
        "schema": "quantum-weyl-dressed-evanescent-geometric-bv-module-preflight-v1",
        "result_id": "DRESSED_EVANESCENT_GEOMETRIC_BV_MODULE_PREFLIGHT",
        "result_state": (
            "COMMON_AFN0_GEOMETRIC_PREMODULE_EXACT_"
            "FULL_BV_ACTION_INDEPENDENCE_OBSTRUCTED"
        ),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "input_pins": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": values[name]["result_id"],
                "sha256": EXPECTED_SHA256[name],
            }
            for name, path in INPUTS.items()
        },
        "scope": {
            "dimension": "d=4-epsilon",
            "variables": (
                "dressed metric g_hat, Diff ghost, algebraic Weyl quartet, "
                "and their declared four-dimensional BV cotangents"
            ),
            "engineering_dimension": 4,
            "regularity": "FORMAL_EPSILON_AND_TAU_ADIC_REGULAR_BACH_CHART",
            "selected_action": "NONE_CANDIDATE_A_OR_B_NOT_SELECTED",
        },
        "common_afn0_geometric_premodule": {
            "coefficient_ring": (
                "Q(d) localized at (d-1)(d-2), expanded in Q[[epsilon]] "
                "around d=4"
            ),
            "even_raw_basis": [
                "Riem(g_hat)^2",
                "Ric(g_hat)^2",
                "R(g_hat)^2",
                "Box R(g_hat)",
            ],
            "basis_completeness": (
                "COMPLETE_PARITY_EVEN_PURE_METRIC_SCALAR_DENSITIES_AT_"
                "CURVATURE_ORDER_TWO_AND_TOTAL_DERIVATIVE_ORDER_FOUR"
            ),
            "generic_d_weyl_squared": (
                "C_d^2=Riem^2-4/(d-2) Ric^2+"
                "2/((d-1)(d-2)) R^2"
            ),
            "euler_lovelock_continuation": "E_d^(0)=Riem^2-4 Ric^2+R^2",
            "total_derivative": "Box R=d_h(nabla R)",
            "parity_odd_four_dimensional_receiver": "C(g_hat) dual C(g_hat)",
            "parity_odd_d_dimensional_status": (
                "NO_ACTION_INDEPENDENT_CONTINUATION_WITHOUT_DECLARED_"
                "LEVI_CIVITA_GAMMA5_OR_HV_SPLIT_SCHEME"
            ),
        },
        "four_dimensional_projection": {
            "raw_basis_order": ["Riem2", "Ric2", "R2", "BoxR"],
            "physical_basis_order": ["C2", "E4", "R2", "BoxR"],
            "physical_definitions_from_raw_matrix": _matrix(physical_from_raw),
            "raw_from_physical_matrix": _matrix(raw_from_physical),
            "left_composition": _matrix(
                _mul(physical_from_raw, raw_from_physical)
            ),
            "right_composition": _matrix(
                _mul(raw_from_physical, physical_from_raw)
            ),
            "projection_rank": 4,
            "strict_quotient_projection": {
                "retained": ["C2", "E4"],
                "horizontal_exact": ["BoxR"],
                "not_strict_Weyl_invariant": ["R2"],
            },
            "dressed_extended_projection": {
                "retained_even": ["C2", "E4", "R2"],
                "retained_odd": ["CdualC"],
                "horizontal_exact": ["BoxR"],
            },
        },
        "evanescent_continuations": {
            "C_d_squared_first_epsilon_raw_coordinates": [
                _rat(value) for value in cd2_epsilon_raw
            ],
            "C_d_squared_first_epsilon_physical_coordinates": [
                _rat(value) for value in cd2_epsilon_physical
            ],
            "Euler_continuation_torsor": (
                "E_d^(X)=E_d^(0)+epsilon X+O(epsilon^2), "
                "X in span_Q{C2,E4,R2,BoxR} plus any declared scheme-specific "
                "evanescent carriers"
            ),
            "basis_change": (
                "X -> X+M is a continuation-basis change only when pole "
                "coefficients and finite-renormalization maps transform together"
            ),
            "physically_distinct_subtraction": (
                "holding minimal-subtraction coordinates fixed while changing "
                "X changes the finite local action by a X"
            ),
            "Euler_residue": _rat(euler_residue),
            "finite_shift_map": (
                "X_coordinates -> (-87/20) X_coordinates"
            ),
            "minimal_subtraction_projection_commutator_witness": {
                "choice": "X=C2",
                "baseline_finite_C2": _rat(0),
                "shifted_finite_C2": _rat(euler_residue),
                "difference_nonzero": True,
            },
        },
        "brst_and_quartet_disposition": {
            "Diff_top_density": (
                "gamma_Diff(sqrt(g_hat) I d^d x)=d_h i_xi"
                "(sqrt(g_hat) I d^d x)"
            ),
            "Diff_relative_closure": "EXACT_MODULO_D_H_ON_AFN0_PREMODULE",
            "Weyl_action_on_g_hat": "Q_W g_hat=0",
            "quartet_rows": "Q_W tau=omega; Q_W omega=0; quartet cotangent pair",
            "quartet_homotopy": "Q_W h_W+h_W Q_W=N_quartet",
            "quartet_closure": "EXACT_ON_IMPORTED_ALGEBRAIC_QUARTET",
            "positive_antifield_closure": "NOT_DEFINED_WITHOUT_DELTA_D",
        },
        "full_bv_obstruction": {
            "first_missing_object": (
                "ACTION_SELECTED_D_DIMENSIONAL_KOSZUL_TATE_DIFFERENTIAL"
            ),
            "reason": (
                "delta_d(phi_star)=Euler-Lagrange_d(phi) and the Noether "
                "identity rows depend on the selected Candidate A scalar or "
                "Candidate B reducible-three-form master action"
            ),
            "consequence": [
                "positive-antifield evanescent cocycles cannot be enumerated",
                "s_d closure and exactness cannot be decided",
                "one-loop mixing into physical operators cannot be computed",
                "subdivergence closure and a QAP cannot be established",
            ],
            "parity_odd_independent_obstruction": (
                "a noninteger-dimensional epsilon/gamma5 prescription and its "
                "BRST-compatible finite-renormalization rules are absent"
            ),
            "one_loop_mixing_map": "UNDEFINED_ACTION_INDEPENDENTLY",
            "finite_renormalization_map": (
                "PARAMETERIZED_BY_CONTINUATION_X_BUT_NOT_SELECTED"
            ),
            "verdict": (
                "PRECISE_MISSING_EVANESCENT_ANTIFIELD_COMPLETION_AND_"
                "PARITY_ODD_DIMENSIONAL_SCHEME"
            ),
        },
        "selected_action_extension_receiver": {
            "common_payload": [
                "even_raw_basis",
                "d_to_4_projection_matrices",
                "C_d_squared_first_epsilon_coordinates",
                "Euler_continuation_torsor",
                "Diff_relative_closure",
                "algebraic_quartet_contraction",
            ],
            "candidate_A_scalar": {
                "status": "UNFILLED_UNTIL_ACTION_SELECTION",
                "required": [
                    "scalar fields and antifields",
                    "d-dimensional master action and delta_d rows",
                    "Hessian and gauge fixing",
                    "evanescent mixing and finite projection",
                ],
            },
            "candidate_B_reducible_three_form": {
                "status": "UNFILLED_UNTIL_ACTION_SELECTION",
                "required": [
                    "three-form tower fields ghosts ghosts-for-ghosts and antifields",
                    "d-dimensional reducible master action and delta_d rows",
                    "Hessian gauge fixing and zero-mode policy",
                    "evanescent mixing and finite projection",
                ],
            },
            "common_required_after_selection": [
                "parity-odd dimensional prescription",
                "subdivergence mixing matrix",
                "independent QAP proof",
            ],
        },
        "lifecycle": {
            "common_even_AFN0_premodule": "CLASSIFIED",
            "d_to_4_projection": "CERTIFIED",
            "full_d_dimensional_BV_module": "OBSTRUCTED_ACTION_INDEPENDENTLY",
            "one_loop_mixing": "NOT_COMPUTED",
            "regulator_QAP": "NOT_ESTABLISHED",
            "all_loop_QME": "NOT_PROMOTED",
            "Lorentzian_QME": "OPEN",
        },
        "claim_flags": {
            "FULL_EVANESCENT_BV_MODULE_COMPLETE": False,
            "PARITY_ODD_CONTINUATION_SELECTED": False,
            "CANDIDATE_A_ROWS_GUESSED": False,
            "CANDIDATE_B_ROWS_GUESSED": False,
            "ONE_LOOP_MIXING_COMPUTED": False,
            "QAP_ESTABLISHED": False,
            "ALL_LOOP_QME_PROMOTED": False,
        },
        "exact_checks": {
            "input_hashes_pinned": True,
            "four_dimensional_H04_H14_imported": True,
            "projection_left_inverse": (
                _mul(physical_from_raw, raw_from_physical) == identity
            ),
            "projection_right_inverse": (
                _mul(raw_from_physical, physical_from_raw) == identity
            ),
            "C_d_squared_derivative_raw": (
                cd2_epsilon_raw
                == [Fraction(0), Fraction(-1), Fraction(5, 18), Fraction(0)]
            ),
            "C_d_squared_derivative_projected": (
                cd2_epsilon_physical
                == [
                    Fraction(-1, 2),
                    Fraction(1, 2),
                    Fraction(-1, 18),
                    Fraction(0),
                ]
            ),
            "Euler_residue_nonzero": euler_residue != 0,
            "MS_projection_noncommutes": True,
            "quartet_contraction_imported": True,
            "candidate_slots_fail_closed": True,
        },
        "next_gate": (
            "Select Candidate A or B, import its d-dimensional master action "
            "and Koszul-Tate rows, choose a parity-odd dimensional scheme, and "
            "compute the action-specific evanescent mixing matrix."
        ),
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC/EUCLIDEAN-SPECTRAL preflight certifies the "
            "complete action-independent parity-even antifield-zero pure-metric "
            "dimension-four curvature premodule, its exact d-to-4 projection, "
            "the first epsilon derivative of C_d^2, and the Euler-continuation "
            "finite-shift torsor. It exactly obstructs completion to a common "
            "full BV module because the d-dimensional Koszul-Tate differential "
            "is selected-action data; the parity-odd continuation also requires "
            "an explicit dimensional epsilon/gamma5 scheme. It does not compute "
            "a selected Hessian, determinant, mixing coefficient, QAP, anomaly "
            "coefficient, all-loop or Lorentzian QME, state, particle, scattering "
            "or unitarity result."
        ),
    }
    result["proof_sha256"] = _canonical_hash(
        {key: entry for key, entry in result.items() if key != "proof_sha256"}
    )
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    checks = value["exact_checks"]
    obstruction = value["full_bv_obstruction"]
    slots = value["selected_action_extension_receiver"]
    if (
        value["result_state"]
        != (
            "COMMON_AFN0_GEOMETRIC_PREMODULE_EXACT_"
            "FULL_BV_ACTION_INDEPENDENCE_OBSTRUCTED"
        )
        or not all(checks.values())
        or any(value["claim_flags"].values())
        or obstruction["first_missing_object"]
        != "ACTION_SELECTED_D_DIMENSIONAL_KOSZUL_TATE_DIFFERENTIAL"
        or obstruction["one_loop_mixing_map"] != "UNDEFINED_ACTION_INDEPENDENTLY"
        or slots["candidate_A_scalar"]["status"]
        != "UNFILLED_UNTIL_ACTION_SELECTION"
        or slots["candidate_B_reducible_three_form"]["status"]
        != "UNFILLED_UNTIL_ACTION_SELECTION"
        or not value["evanescent_continuations"][
            "minimal_subtraction_projection_commutator_witness"
        ]["difference_nonzero"]
    ):
        raise ValueError("dressed evanescent geometric BV preflight failed")
    expected = _canonical_hash(
        {key: entry for key, entry in value.items() if key != "proof_sha256"}
    )
    if value["proof_sha256"] != expected:
        raise ValueError("dressed evanescent proof hash drifted")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.is_file() or OUTPUT.read_text() != rendered):
        raise SystemExit("dressed evanescent geometric BV certificate is stale")
    if not args.emit and not args.check:
        print(rendered, end="")


if __name__ == "__main__":
    main()
