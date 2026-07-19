"""Certify isolated candidate 4 from the exact product q2 PBW payload.

The evaluator first reproduces the frozen opposite-momentum L=4 source
exactly.  It then evaluates the first cross-|n| candidate with two q-minus
axial inputs and pairs the polar L=4 source against the complete p-primary
cokernel.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from functools import lru_cache
from math import factorial
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor import (
    _action_operator,
)


ROOT = Path(__file__).resolve().parents[2]
Q2 = ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/q2.json"
SLICE = ROOT / "bridge/einstein_sector/generated/einstein_maxwell_weyl_ell2_axial_qminus_pair_L4_q2_slice.json"
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate4_bounded_obstruction.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate4_bounded_obstruction.schema.json"
INPUTS = {
    "candidate_ledger": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_isolated_candidates.json",
    "parity_workload": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_parity_workload.json",
    "polar_operator": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_full_tensor.json",
    "opposite_momentum_calibration": ROOT / "bridge/certificates/einstein_maxwell_weyl_twist_aligned_opposite_momentum_bounded_obstruction.json",
    "q2_slice": SLICE,
}
SUPPORTED_INPUTS = {9, 12, 16, 17}
OUTPUT_ORDERS = {20: (0, 2, 4), 21: (0, 2, 4), 24: (0, 2, 4), 33: (1, 3)}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: sp.Expr) -> sp.Expr:
    return sp.factor(sp.simplify(sp.sqrtdenest(sp.radsimp(value))))


def _multinomial(total: int, first: int, second: int) -> int:
    third = total - first - second
    return factorial(total) // (factorial(first) * factorial(second) * factorial(third))


theta = sp.symbols("theta", real=True)
Y = sp.legendre(2, sp.cos(theta))
X = -sp.sin(theta) * sp.diff(Y, theta)


@lru_cache(maxsize=None)
def angular_derivative(row: int, order: int) -> sp.Expr:
    function = X if row in (9, 12) else Y
    return sp.simplify(sp.diff(function, theta, order).subs(theta, sp.pi / 2))


def mode_derivative(row: int, word: tuple[int, ...], momentum: sp.Expr, frequency: sp.Expr) -> sp.Expr:
    if 3 in word:
        return sp.S.Zero
    time_order = word.count(0)
    space_order = word.count(1)
    theta_order = word.count(2)
    root = 2 * sp.sqrt(3)
    amplitude = {
        9: 2 * momentum,
        12: -2 * frequency,
        16: -root * momentum,
        17: root * frequency,
    }[row]
    return amplitude * (-sp.I * frequency) ** time_order * (sp.I * momentum) ** space_order * angular_derivative(row, theta_order)


def load_relevant() -> tuple[list[dict[str, object]], list[dict[int, sp.Expr]]]:
    content = json.loads(Q2.read_text())["content"]
    profiles: list[dict[int, sp.Expr]] = []
    for profile in content["coefficient_profiles"]:
        values = {}
        for item in profile["coefficient_jets"]:
            word = item["word"]
            if any(axis != 2 for axis in word):
                raise AssertionError(f"non-theta coefficient jet: {word}")
            values[len(word)] = sp.Rational(item["coefficient"])
        profiles.append(values)
    terms = [
        term for term in content["terms"]
        if term["output_row"] in OUTPUT_ORDERS
        and term["inputs"][0]["row"] in SUPPORTED_INPUTS
        and term["inputs"][1]["row"] in SUPPORTED_INPUTS
    ]
    assert len(terms) == 842
    return terms, profiles


def source_jets(k_1: sp.Expr, omega_1: sp.Expr, k_2: sp.Expr, omega_2: sp.Expr) -> dict[int, dict[int, sp.Expr]]:
    terms, profiles = load_relevant()
    output: dict[tuple[int, int], sp.Expr] = defaultdict(lambda: sp.S.Zero)
    for term in terms:
        row = int(term["output_row"])
        first, second = term["inputs"]
        first_row, second_row = int(first["row"]), int(second["row"])
        first_word, second_word = tuple(first["word"]), tuple(second["word"])
        profile = profiles[int(term["coefficient_profile"])]
        for output_order in OUTPUT_ORDERS[row]:
            value = sp.S.Zero
            for coefficient_order in range(output_order + 1):
                coefficient_jet = profile.get(coefficient_order, sp.S.Zero)
                if coefficient_jet == 0:
                    continue
                for first_extra in range(output_order - coefficient_order + 1):
                    second_extra = output_order - coefficient_order - first_extra
                    value += (
                        _multinomial(output_order, coefficient_order, first_extra)
                        * coefficient_jet
                        * mode_derivative(first_row, first_word + (2,) * first_extra, k_1, omega_1)
                        * mode_derivative(second_row, second_word + (2,) * second_extra, k_2, omega_2)
                    )
            output[(row, output_order)] += value
    return {
        row: {order: sp.factor(sp.expand(output[(row, order)])) for order in orders}
        for row, orders in OUTPUT_ORDERS.items()
    }


def scalar_l4(jets: dict[int, sp.Expr]) -> sp.Expr:
    coefficients = sp.symbols("c0 c2 c4")
    ansatz = sum(
        coefficient * sp.legendre(ell, sp.cos(theta))
        for coefficient, ell in zip(coefficients, (0, 2, 4), strict=True)
    )
    equations = [
        sp.Eq(sp.diff(ansatz, theta, order).subs(theta, sp.pi / 2), jets[order])
        for order in (0, 2, 4)
    ]
    solution = sp.solve(equations, coefficients, dict=True)
    assert len(solution) == 1
    return sp.factor(solution[0][coefficients[2]])


def vector_l4(jets: dict[int, sp.Expr]) -> sp.Expr:
    coefficients = sp.symbols("c2 c4")
    ansatz = sum(
        coefficient
        * (-sp.diff(sp.legendre(ell, sp.cos(theta)), theta))
        / sp.sin(theta)
        for coefficient, ell in zip(coefficients, (2, 4), strict=True)
    )
    equations = [
        sp.Eq(sp.diff(ansatz, theta, order).subs(theta, sp.pi / 2), jets[order])
        for order in (1, 3)
    ]
    solution = sp.solve(equations, coefficients, dict=True)
    assert len(solution) == 1
    return sp.factor(solution[0][coefficients[1]])


def reduced_source(k_1: sp.Expr, omega_1: sp.Expr, k_2: sp.Expr, omega_2: sp.Expr) -> sp.Matrix:
    jets = source_jets(k_1, omega_1, k_2, omega_2)
    # The metric Taylor rows are variational densities and carry the
    # diagonal-field factor 1/2 (and the off-diagonal multiplicity already
    # built into row 21).  Restore the action-row normalization used by H_P.
    return sp.Matrix([
        2 * scalar_l4(jets[20]),
        2 * scalar_l4(jets[21]),
        2 * scalar_l4(jets[24]),
        40 * vector_l4(jets[33]),
    ]).applyfunc(sp.factor)


def extract_slice() -> dict[str, object]:
    """Extract the four symbolic action rows from the parent q2 payload."""

    k_1, omega_1, k_2, omega_2 = sp.symbols(
        "k_1 omega_1 k_2 omega_2", real=True
    )
    source = reduced_source(k_1, omega_1, k_2, omega_2)
    product_path = ROOT / "bridge/certificates/WEYL_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1.json"
    product = json.loads(product_path.read_text())
    return {
        "schema": "einstein-maxwell-weyl-ell2-axial-qminus-pair-L4-q2-slice-v1",
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_AXIAL_QMINUS_PAIR_L4_Q2_SLICE",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "parent": {
            "result_id": product["result_id"],
            "q2_sha256": sha(Q2),
            "row_layout_sha256": product["executable_contract"]["row_layout_sha256"],
            "action_sha256": product["executable_contract"]["action_sha256"],
        },
        "scope": {
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "carrier": "two axisymmetric axial ell=2 Einstein q-minus representatives at arbitrary signed momenta and positive frequencies",
            "degree": 2,
            "parity": "axial times axial input; polar L=4 output",
            "ell": "2 times 2 -> 4",
            "m": "0+0 -> 0",
            "k": "arbitrary signed k_1,k_2",
            "omega": "arbitrary omega_1,omega_2 before shell specialization",
        },
        "pbw_support": {
            "input_rows": [9, 12, 16, 17],
            "output_rows": [20, 21, 24, 33],
            "relevant_q2_terms": 842,
            "coefficient_jet_order": 4,
            "scalar_density_basis": "P_L(cos(theta))",
            "contravariant_axial_basis": "-partial_theta P_L(cos(theta))/sin(theta)",
        },
        "variables": ["k_1", "omega_1", "k_2", "omega_2"],
        "source_action_row_order": ["-metric_00", "2*metric_01", "-metric_11", "2*20*maxwell_axial"],
        "source_action_rows": [str(sp.factor(value)) for value in source],
        "claim_boundary": "This content-addressed slice records only the symbolic polar L=4 action source from two axial ell=2 q-minus representatives. It is not the full q2 export and does not classify other parities, branches, output harmonics or correction classes.",
    }


def slice_source(k_1: sp.Expr, omega_1: sp.Expr, k_2: sp.Expr, omega_2: sp.Expr) -> sp.Matrix:
    value = json.loads(SLICE.read_text())
    if value["result_id"] != "EINSTEIN_MAXWELL_WEYL_ELL2_AXIAL_QMINUS_PAIR_L4_Q2_SLICE":
        raise AssertionError("candidate-4 q2 slice identity changed")
    support = value["pbw_support"]
    if support["relevant_q2_terms"] != 842 or support["coefficient_jet_order"] != 4:
        raise AssertionError("candidate-4 q2 slice support changed")
    local = {
        "k_1": k_1,
        "omega_1": omega_1,
        "k_2": k_2,
        "omega_2": omega_2,
        "sqrt": sp.sqrt,
    }
    return sp.Matrix([
        sp.sympify(row, locals=local) for row in value["source_action_rows"]
    ]).applyfunc(sp.factor)


def calculation() -> dict[str, object]:
    tuned_k = sp.sqrt(2 * sp.sqrt(3) - sp.Rational(7, 6))
    tuned_omega = sp.sqrt(sp.Rational(29, 6))
    calibrated = slice_source(tuned_k, tuned_omega, -tuned_k, tuned_omega)
    expected = sp.Matrix([
        -sp.Rational(64, 7) * (163 + 261 * sp.sqrt(3)),
        0,
        sp.Rational(32, 105) * (-21293 + 9450 * sp.sqrt(3)),
        sp.Rational(384, 7) * (-137 + 55 * sp.sqrt(3)),
    ])
    if (calibrated - expected).applyfunc(canonical) != sp.zeros(4, 1):
        raise AssertionError(f"opposite-momentum calibration failed: {calibrated}")

    rho = sp.Rational(29) * (-361 + 783 * sp.sqrt(3)) / 26772
    offset = 6 - 2 * sp.sqrt(3)
    k_1, k_2 = sp.sqrt(rho), -2 * sp.sqrt(rho)
    omega_1, omega_2 = sp.sqrt(rho + offset), sp.sqrt(4 * rho + offset)
    output_momentum = k_1 + k_2
    output_frequency = omega_1 + omega_2
    shell_defect = canonical(
        output_frequency**2 - output_momentum**2 - sp.Rational(58, 3)
    )
    if shell_defect != 0:
        raise AssertionError(f"candidate 4 left the polar p shell: {shell_defect}")
    candidate = slice_source(k_1, omega_1, k_2, omega_2)

    # On the L=4 p shell, these span the full two-dimensional left kernel of
    # the symmetric action Hessian.  Keeping them in rational (K,Omega) form
    # avoids encoding a basis artifact from radical Gaussian elimination.
    adjoints = sp.Matrix.hstack(
        sp.Matrix([
            1,
            -(3 * output_momentum**2 + 29)
            / (3 * output_momentum * output_frequency),
            1,
            0,
        ]),
        sp.Matrix([
            sp.Rational(4, 3),
            -2 * (output_momentum**2 + 20)
            / (3 * output_momentum * output_frequency),
            0,
            1,
        ]),
    )
    action, (target_lambda, target_momentum, target_frequency) = _action_operator()
    block = action.subs({
        target_lambda: 20,
        target_momentum: output_momentum,
        target_frequency: output_frequency,
    })
    kernel_defect = (block.T * adjoints).applyfunc(canonical)
    if kernel_defect != sp.zeros(4, 2):
        raise AssertionError(f"candidate 4 cokernel basis failed: {kernel_defect}")
    if block.rank() != 2 or adjoints.rank() != 2:
        raise AssertionError("candidate 4 p-primary cokernel dimension changed")

    pairings = (adjoints.T * candidate).applyfunc(canonical)
    expected_nonzero = -sp.Rational(1152, 203) * (-265 + 149 * sp.sqrt(3))
    if canonical(pairings[0]) != 0 or canonical(pairings[1] - expected_nonzero) != 0:
        raise AssertionError(f"candidate 4 pairings changed: {pairings}")
    norm_witness = 265**2 - 3 * 149**2
    if norm_witness != 3622:
        raise AssertionError("candidate 4 nonzero norm witness changed")

    return {
        "rho": rho,
        "k_1": k_1,
        "k_2": k_2,
        "omega_1": omega_1,
        "omega_2": omega_2,
        "K": output_momentum,
        "Omega": output_frequency,
        "shell_defect": shell_defect,
        "calibration": calibrated,
        "source": candidate,
        "block": block,
        "adjoints": adjoints,
        "kernel_defect": kernel_defect,
        "pairings": pairings,
        "nonzero_pairing": expected_nonzero,
        "norm_witness": norm_witness,
    }


def matrix_strings(matrix: sp.MatrixBase) -> list[list[str]]:
    return [
        [str(canonical(matrix[row, column])) for column in range(matrix.cols)]
        for row in range(matrix.rows)
    ]


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    candidates = records["candidate_ledger"]["candidate_ledger"]["rows"]
    row = candidates[3]
    if not (
        row["first_branch"] == row["second_branch"] == "q_minus"
        and row["target_branch"] == "p_extra"
        and row["output_ell"] == 4
        and row["canonical_signed_momenta"] == [1, -2]
        and row["admissible_temporal_channel"] == "SUM"
    ):
        raise AssertionError(f"isolated candidate 4 changed: {row}")
    workload = records["parity_workload"]["source_workload"]["rows"][3]
    axial_axial = workload["parity_channels"][0]
    if axial_axial != {
        "first_parity": "axial",
        "second_parity": "axial",
        "target_parity": "polar",
        "angular_witness_m1_m2_M_3j": [0, 0, 0, "sqrt(70)/35"],
        "axisymmetric_fixture_available": True,
        "reduced_scalar_source_coefficients": 2,
    }:
        raise AssertionError(f"candidate 4 parity workload changed: {axial_axial}")
    q2_slice = records["q2_slice"]
    if q2_slice["parent"]["q2_sha256"] != "be4d163044138f4b3b093c54527c2484cfac9eea48a58c791e97926be8597fec":
        raise AssertionError("candidate-4 q2 parent hash changed")
    data = calculation()
    source = data["source"]
    adjoints = data["adjoints"]
    pairings = data["pairings"]
    assert isinstance(source, sp.MatrixBase)
    assert isinstance(adjoints, sp.MatrixBase)
    assert isinstance(pairings, sp.MatrixBase)
    return {
        "schema": "einstein-maxwell-weyl-ell2-two-abs-momentum-candidate4-bounded-obstruction-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_CANDIDATE4_BOUNDED_OBSTRUCTION",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G1_EXPLICIT_ELL2_TWO_ABS_MOMENTUM_FIXTURE",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 at the candidate-4 algebraic circumference",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "two positive-frequency axial Einstein q-minus modes on |n|=1 and |n|=2",
            "degree": 2,
            "parity": "axial times axial input; polar p-primary output",
            "ell": "input ell=2,m=0 times ell=2,m=0; output L=4,M=0",
            "m": "0,0 -> 0",
            "k": "k_1=sqrt(rho), k_2=-2sqrt(rho), K=-sqrt(rho)",
            "omega": "SUM channel Omega=omega_1+omega_2 on the polar p shell",
        },
        "candidate": {
            "candidate_index": 4,
            "rho": str(data["rho"]),
            "k_1": str(data["k_1"]),
            "k_2": str(data["k_2"]),
            "omega_1": str(data["omega_1"]),
            "omega_2": str(data["omega_2"]),
            "K": str(data["K"]),
            "Omega": str(data["Omega"]),
            "p_shell_defect": str(data["shell_defect"]),
        },
        "pbw_projection": {
            "input_rows": [9, 12, 16, 17],
            "output_rows": [20, 21, 24, 33],
            "relevant_q2_terms": 842,
            "coefficient_jet_order": 4,
            "slice_path": str(SLICE.relative_to(ROOT)),
            "parent_q2_sha256": q2_slice["parent"]["q2_sha256"],
            "parent_row_layout_sha256": q2_slice["parent"]["row_layout_sha256"],
            "parent_action_sha256": q2_slice["parent"]["action_sha256"],
            "scalar_density_basis": "P_L(cos(theta))",
            "contravariant_axial_basis": "-partial_theta P_L(cos(theta))/sin(theta)",
            "action_row_order": ["-metric_00", "2*metric_01", "-metric_11", "2*20*maxwell_axial"],
            "opposite_momentum_calibration_source": [str(canonical(value)) for value in data["calibration"]],
            "opposite_momentum_calibration_exact": True,
        },
        "quadratic_source": {
            "convention": "the cross coefficient in (1/2)D^2E[u_1+u_2,u_1+u_2]=D^2E[u_1,u_2]",
            "source_action_rows": [str(canonical(value)) for value in source],
        },
        "polar_p_cokernel": {
            "target_block_rank": 2,
            "cokernel_dimension": 2,
            "adjoint_columns": matrix_strings(adjoints),
            "kernel_defect": matrix_strings(data["kernel_defect"]),
            "pairings": [str(canonical(value)) for value in pairings],
            "nonzero_pairing": str(data["nonzero_pairing"]),
            "quadratic_field_norm_witness": data["norm_witness"],
        },
        "second_order_verdict": {
            "correction_class": "BOUNDED_OR_FINITE_QUASIPERIODIC",
            "status": "OBSTRUCTED",
            "reason": "one complete polar p-primary adjoint-cokernel functional is nonzero",
            "smooth_secular_status": "OPEN",
            "causal_retarded_status": "NO_CERTIFIED_MAP",
        },
        "workload_progress": {
            "candidate_4_axial_axial_coefficients_resolved": 2,
            "axisymmetric_L4_coefficients_total": 108,
            "remaining_axisymmetric_L4_coefficients": 106,
            "complete_two_fibre_tangent_cone_classified": False,
        },
        "classification": {
            "candidate_4_exact_source_computed": True,
            "frozen_opposite_momentum_fixture_reproduced_exactly": True,
            "complete_p_primary_cokernel_paired": True,
            "one_pairing_zero": True,
            "one_pairing_nonzero": True,
            "bounded_candidate_4_obstructed": True,
            "all_candidate_rows_classified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The first computed cross-|n| source does not evade the bounded resonance gate: its polar L=4 p-primary source has a nonzero cokernel component. The equality of the surviving pairing with the earlier opposite-momentum fixture is an exact output, not an assumed normalization.",
        "next_gate": "batch the remaining 106 axisymmetric L=4 reduced adjoint coefficients before constructing the nonaxisymmetric L=1,3 fixtures",
        "claim_boundary": "This certifies one axial-axial candidate-4 bounded obstruction and two of the 108 axisymmetric L=4 workload coefficients. It does not classify the other parity or branch channels, arbitrary finite harmonic sums, smooth secular corrections, causal/retarded corrections, residual descent, observables or quantum states.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
                for name, path in INPUTS.items()
            },
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_candidate4_pbw_probe --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_ell2_two_abs_momentum_candidate4_bounded_obstruction.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_ell2_two_abs_momentum_candidate4_bounded_obstruction",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--extract-slice", action="store_true")
    args = parser.parse_args()
    if args.extract_slice:
        SLICE.parent.mkdir(parents=True, exist_ok=True)
        SLICE.write_text(json.dumps(extract_slice(), indent=2, sort_keys=True) + "\n")
        print("EINSTEIN_MAXWELL_WEYL_ELL2_AXIAL_QMINUS_PAIR_L4_Q2_SLICE: PASS")
        return
    value = build()
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    elif json.loads(OUTPUT.read_text()) != value:
        raise AssertionError("stale candidate-4 bounded-obstruction certificate")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_CANDIDATE4_BOUNDED_OBSTRUCTION: PASS")


if __name__ == "__main__":
    main()
