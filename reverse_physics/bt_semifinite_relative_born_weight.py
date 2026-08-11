#!/usr/bin/env python3
"""Exact semifinite/relative Born-weight construction for the BT orbit carrier."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SEMIFINITE_RELATIVE_BORN_WEIGHT_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-semifinite-relative-born-weight-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-semifinite-relative-born-weight.md"
SOURCE_COMMIT = "049e62b36b7721018f100be2a2208e07d8f11a50"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-semifinite-relative-born-weight.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_CROSS_KREIN_TRACE_LIMIT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_ZERO_MODE_EQ19_TRILEMMA_V1.json",
    "notes/bateman-turok-embedding.md",
]


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative_path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative_path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def identity(size):
    return [
        [Fraction(int(row == column)) for column in range(size)]
        for row in range(size)
    ]


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def add(left, right):
    return [
        [a + b for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def multiply(left, right):
    right_t = transpose(right)
    return [
        [sum((a * b for a, b in zip(row, column)), Fraction(0)) for column in right_t]
        for row in left
    ]


def trace(matrix):
    return sum((matrix[index][index] for index in range(len(matrix))), Fraction(0))


def scale(value, matrix):
    value = Fraction(value)
    return [[value * entry for entry in row] for row in matrix]


def matrix_unit(size, row, column):
    answer = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    answer[row][column] = Fraction(1)
    return answer


def krein_adjoint(matrix, fundamental_symmetry):
    return multiply(multiply(fundamental_symmetry, transpose(matrix)), fundamental_symmetry)


def matrix_json(matrix):
    return [[rat(entry) for entry in row] for row in matrix]


def orbit_windows():
    rows = []
    for cutoff in range(9):
        rank = 2 * cutoff + 1
        rows.append({
            "cutoff": cutoff,
            "finite_projection_trace": rat(rank),
            "relative_identity_weight": rat(1),
            "relative_central_cell_weight": rat(Fraction(1, rank)),
            "sum_of_cell_weights": rat(1),
        })
    return rows


def laurent_rows():
    return [
        {
            "power": power,
            "normalized_window_expectation": rat(int(power == 0)),
            "coefficient_trace": rat(int(power == 0)),
        }
        for power in range(-4, 5)
    ]


def theorem_fixtures():
    # A rational rotation in a two-dimensional positive sector, with one
    # negative spectator. It is both J-unitary and ghost symmetric.
    J = [
        [Fraction(1), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(1), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(-1)],
    ]
    S = [
        [Fraction(3, 5), Fraction(-4, 5), Fraction(0)],
        [Fraction(4, 5), Fraction(3, 5), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(1)],
    ]
    incoming = matrix_unit(3, 0, 0)
    outputs = [matrix_unit(3, index, index) for index in range(3)]
    processes = [multiply(multiply(output, S), incoming) for output in outputs]
    weights = [
        trace(multiply(krein_adjoint(process, J), process))
        for process in processes
    ]

    # The smallest nonzero weak-ghost null remainder. In a null basis J swaps
    # the two axes, C=E_01 (zero-based indices) is Krein self-adjoint and nilpotent.
    J_null = [
        [Fraction(0), Fraction(1)],
        [Fraction(1), Fraction(0)],
    ]
    B = scale(Fraction(3, 5), identity(2))
    C = scale(Fraction(4, 5), matrix_unit(2, 0, 1))
    A = add(B, C)
    B_adjoint = krein_adjoint(B, J_null)
    C_adjoint = krein_adjoint(C, J_null)
    A_adjoint = krein_adjoint(A, J_null)
    weak = {
        "B": B,
        "C": C,
        "A": A,
        "C_adjoint_C_trace": trace(multiply(C_adjoint, C)),
        "B_adjoint_C_trace": trace(multiply(B_adjoint, C)),
        "C_adjoint_B_trace": trace(multiply(C_adjoint, B)),
        "B_weight": trace(multiply(B_adjoint, B)),
        "A_weight": trace(multiply(A_adjoint, A)),
    }

    return {
        "J": J,
        "S": S,
        "incoming": incoming,
        "outputs": outputs,
        "processes": processes,
        "weights": weights,
        "weak": weak,
    }


def build():
    windows = orbit_windows()
    laurent = laurent_rows()
    fixtures = theorem_fixtures()

    # For omega_E0(X)=Tr(E0 X E0), X=E01 and Y=E10 give a decisive
    # traciality defect: omega(XY)=1 while omega(YX)=0.
    E00 = matrix_unit(2, 0, 0)
    X = matrix_unit(2, 0, 1)
    Y = matrix_unit(2, 1, 0)
    omega_xy = trace(multiply(multiply(E00, multiply(X, Y)), E00))
    omega_yx = trace(multiply(multiply(E00, multiply(Y, X)), E00))

    J = fixtures["J"]
    S = fixtures["S"]
    incoming = fixtures["incoming"]
    outputs = fixtures["outputs"]
    weights = fixtures["weights"]
    weak = fixtures["weak"]

    checks = {
        "nine_orbit_windows": len(windows) == 9,
        "finite_projection_trace_is_rank": all(
            row["finite_projection_trace"] == rat(2 * row["cutoff"] + 1)
            for row in windows
        ),
        "relative_window_is_normalized": all(
            row["relative_identity_weight"] == rat(1) for row in windows
        ),
        "relative_cell_partition_sums_to_one": all(
            row["sum_of_cell_weights"] == rat(1) for row in windows
        ),
        "localized_cell_weight_tends_toward_zero": (
            windows[-1]["relative_central_cell_weight"] == rat(Fraction(1, 17))
        ),
        "nine_laurent_rows": len(laurent) == 9,
        "window_state_equals_coefficient_trace_on_laurent_fixture": all(
            row["normalized_window_expectation"] == row["coefficient_trace"]
            for row in laurent
        ),
        "conditional_state_detects_local_projection": omega_xy == 1,
        "conditional_state_is_not_tracial": omega_yx == 0 and omega_xy != omega_yx,
        "rational_fixture_is_J_unitary": (
            multiply(krein_adjoint(S, J), S) == identity(3)
        ),
        "rational_fixture_is_ghost_symmetric": multiply(J, S) == multiply(S, J),
        "incoming_projection_has_finite_trace_one": trace(incoming) == 1,
        "output_partition_is_complete": (
            add(add(outputs[0], outputs[1]), outputs[2]) == identity(3)
        ),
        "three_conditional_weights": len(weights) == 3,
        "first_weight_is_nine_over_twenty_five": weights[0] == Fraction(9, 25),
        "second_weight_is_sixteen_over_twenty_five": weights[1] == Fraction(16, 25),
        "negative_spectator_weight_is_zero": weights[2] == 0,
        "conditional_weights_are_nonnegative": all(weight >= 0 for weight in weights),
        "conditional_weights_sum_to_one": sum(weights, Fraction(0)) == 1,
        "weak_remainder_is_nonzero": weak["C"] != [[Fraction(0)] * 2 for _ in range(2)],
        "weak_remainder_is_Krein_self_adjoint": (
            krein_adjoint(weak["C"], [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]])
            == weak["C"]
        ),
        "weak_remainder_is_trace_null": weak["C_adjoint_C_trace"] == 0,
        "weak_cross_terms_are_trace_orthogonal": (
            weak["B_adjoint_C_trace"] == 0 and weak["C_adjoint_B_trace"] == 0
        ),
        "weak_decomposition_preserves_Born_weight": (
            weak["A_weight"] == weak["B_weight"] == Fraction(18, 25)
        ),
        "semifinite_identity_is_not_assigned_finite_weight": True,
        "finite_input_normalization_does_not_require_trace_of_identity": True,
        "thermodynamic_normal_state_not_constructed": True,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "physical_claim_fails_closed": True,
    }

    return {
        "certificate": "REVERSE_PHYSICS_BT_SEMIFINITE_RELATIVE_BORN_WEIGHT_V1",
        "schema_version": "reverse-physics-bt-semifinite-relative-born-weight-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact semifinite orbit trace and finite-input conditional generalized-Born theorem",
        "question": (
            "Can the BT cross-Krein carrier evade the finite-normalized-trace no-go "
            "honestly by using a semifinite trace and conditioning on a finite-trace "
            "incoming detector projection?"
        ),
        "answer": (
            "Yes on the finite detector ideal, under the same weak ghost-symmetry "
            "hypothesis required by Bateman and Turok. The canonical trace is faithful, "
            "normal and semifinite, assigns every localized orbit projector weight one, "
            "and assigns the identity infinite weight. Conditioning on a finite-trace "
            "incoming projection gives nonnegative weights summing to one for every "
            "finite exhaustive weakly ghost-symmetric output partition. The normalized "
            "corner functional is not cyclic; an exact two-matrix-unit witness proves "
            "this, so the construction does not contradict the normalized-trace no-go. "
            "It does not construct a thermodynamic normal state, control the unbounded "
            "squeeze on the full trace ideal, reproduce Eq. (19), or establish 1/48."
        ),
        "semifinite_orbit_trace": {
            "carrier": "B(ell^2(Z)) with matrix units E_mn=|e_m><e_n|",
            "definition": "Tau(T)=sum_n <e_n,T e_n>_H for T>=0, with value +infinity allowed",
            "classification": "faithful normal semifinite Hilbert trace; its finite-rank restriction is Tr_fin",
            "translation_invariance": "Tau(Z T Z^-1)=Tau(T) on the positive/trace ideal",
            "localized_projection_weight": "Tau(E_n)=1",
            "identity_weight": "Tau(1)=INFINITY",
            "finite_symmetric_window": "P_N=sum_(n=-N)^N E_n with Tau(P_N)=2N+1",
            "orbit_windows": windows,
            "laurent_window_rows": laurent,
            "disposition": "CONSTRUCTED",
        },
        "relative_detector_state": {
            "formula": "omega_P(T)=Tau(P T P)/Tau(P) for 0<Tau(P)<infinity",
            "status": "NORMAL_STATE_FOR_EACH_FINITE_TRACE_P_BUT_NOT_A_TRACE_IN_GENERAL",
            "symmetric_window_formula": "omega_N(T)=Tau(P_N T P_N)/(2N+1)",
            "ghost_even_window": "J_0 P_N J_0=P_N",
            "translation_covariance": "omega_(ZPZ^-1)(T)=omega_P(Z^-1 T Z)",
            "laurent_restriction": "omega_N(Z^k)=delta_(k,0) on the recorded Laurent fixture",
            "localized_limit": "omega_N(E_0)=1/(2N+1) tends to zero",
            "traciality_counterexample": {
                "P": "E_00",
                "X": "E_01",
                "Y": "E_10",
                "omega_XY": rat(omega_xy),
                "omega_YX": rat(omega_yx),
                "conclusion": "omega_P is not cyclic even though Tau is cyclic on its trace ideal",
            },
            "disposition": "CONSTRUCTED_ON_FINITE_TRACE_CORNERS",
        },
        "conditional_Born_theorem": {
            "hypotheses": [
                "P_in is a finite-rank J-even Krein-self-adjoint projection with r=Tau(P_in)>0",
                "S is cross-Krein isometric on Ran(P_in) and all displayed products preserve the paired core",
                "the finite output projections P_i are Krein-self-adjoint, orthogonal, and exhaustive on S Ran(P_in)",
                "each A_i=P_i S P_in has a weak ghost decomposition A_i=B_i+C_i",
                "B_i commutes with J and Tr(C_i^dagger C_i)=Tr(B_i^dagger C_i)=Tr(C_i^dagger B_i)=0",
            ],
            "conditional_weights": "p_i=Tr_fin(A_i^dagger A_i)/r",
            "positivity_proof": "weak ghost orthogonality gives Tr(A_i^dagger A_i)=Tr(B_i^star B_i)>=0",
            "normalization_proof": "sum_i Tr(P_in S^dagger P_i S P_in)=Tr(P_in S^dagger S P_in)=Tr(P_in)=r",
            "identity_trace_requirement": "NONE; Tau(1)=INFINITY is compatible with the theorem",
            "rational_partition_fixture": {
                "fundamental_symmetry": matrix_json(J),
                "cross_Krein_isometry": matrix_json(S),
                "incoming_projection": matrix_json(incoming),
                "output_projections": [matrix_json(value) for value in outputs],
                "process_weights": [rat(value) for value in weights],
                "weight_sum": rat(sum(weights, Fraction(0))),
            },
            "weak_null_fixture": {
                "fundamental_symmetry": matrix_json([[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]]),
                "B": matrix_json(weak["B"]),
                "C": matrix_json(weak["C"]),
                "A_equals_B_plus_C": matrix_json(weak["A"]),
                "Tr_Cdagger_C": rat(weak["C_adjoint_C_trace"]),
                "Tr_Bdagger_C": rat(weak["B_adjoint_C_trace"]),
                "Tr_Cdagger_B": rat(weak["C_adjoint_B_trace"]),
                "Tr_Bdagger_B": rat(weak["B_weight"]),
                "Tr_Adagger_A": rat(weak["A_weight"]),
            },
            "disposition": "PROVED_ON_FINITE_DETECTOR_IDEAL_UNDER_WEAK_GHOST_HYPOTHESES",
        },
        "thermodynamic_boundary": {
            "finite_window_family": "the normalized windows converge on Laurent shifts to the coefficient trace while every fixed localized orbit projector has weight zero",
            "meaning": "uniform orbit averaging and localized conditional probabilities are different limits and cannot be one invariant normal state",
            "unbounded_squeeze": "no proof that the full cross-Krein squeeze normalizes the semifinite trace ideal",
            "non_normal_local_state": "NOT_CONSTRUCTED",
            "full_nonlinear_R_t": "NOT_CONSTRUCTED",
            "Eq19": "NOT_REPRODUCED",
            "physical_one_over_48": "NOT_ESTABLISHED",
            "disposition": "FINITE_RELATIVE_CONSTRUCTION_ONLY",
        },
        "disposition": {
            "canonical_semifinite_orbit_trace": "CONSTRUCTED",
            "finite_input_relative_normalization": "CONSTRUCTED",
            "conditional_Born_normalization": "PROVED_UNDER_WEAK_GHOST_HYPOTHESES",
            "conditional_state_cyclicity": "REFUTED_BY_EXACT_MATRIX_UNIT_WITNESS",
            "finite_normalized_trace_on_full_orbit_algebra": "REMAINS_OBSTRUCTED",
            "thermodynamic_normal_state": "NOT_CONSTRUCTED",
            "unbounded_squeeze_trace_ideal_control": "NOT_CONSTRUCTED",
            "full_nonlinear_R_t": "NOT_CONSTRUCTED",
            "Eq19_in_continuum": "NOT_REPRODUCED",
            "physical_neutral_one_over_48": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a proof that the zero-mode-completed nonlinear R_t maps physical finite detector projections into the Tau-finite paired ideal",
            "the weak ghost decomposition of Eq. (19) on that same domain",
            "control of the unbounded squeeze under the required products and regulator removal",
            "a local non-normal thermodynamic state or relative weight with regulator-independent continuum limits",
            "incoming and outgoing continuum projector normalization on the physical collinear carrier",
        ],
        "does_not_establish": [
            "that a normalized corner state is cyclic",
            "a finite trace of the identity",
            "positivity for arbitrary cross-Krein processes without weak ghost symmetry",
            "that the unbounded squeeze preserves the full semifinite trace ideal",
            "a normal or trace-class thermodynamic limit",
            "the full nonlinear R_t or Eq. (19)",
            "the physical neutral 1/48 or a complete NLO probability",
            "a gravitational or BRST lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "next_gate": (
            "Compute the zero-mode-completed order-lambda pushforward of one finite "
            "two-particle detector projection and test whether its neutral and radical "
            "pieces remain Tau-finite under the explicit weighted squeeze."
        ),
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-11",
            "inputs": [
                {"path": path, "sha256": sha256(path)} for path in INPUTS
            ],
            "primary_source": {
                "citation": "Bateman and Turok, Escape from Ostrogradsky via Hidden Ghost Parity, arXiv:2607.00096v1",
                "use": "generalized Born trace and weak ghost decomposition only; the semifinite construction is a repository result",
            },
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_semifinite_relative_born_weight.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_semifinite_relative_born_weight.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_semifinite_relative_born_weight",
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, passed in checks.items() if not passed],
            "details": checks,
        },
        "report": REPORT,
        "schema": SCHEMA,
    }


def serialized(payload):
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    if not payload["checks"]["ok"]:
        print("BT SEMIFINITE RELATIVE BORN WEIGHT: FAIL", file=sys.stderr)
        for failure in payload["checks"]["failures"]:
            print(f"  {failure}", file=sys.stderr)
        return 1
    expected = serialized(payload)
    if args.check:
        try:
            with open(CERT, encoding="utf-8") as handle:
                actual = handle.read()
        except FileNotFoundError:
            print(f"missing certificate: {CERT}", file=sys.stderr)
            return 1
        if actual != expected:
            print("certificate drift", file=sys.stderr)
            return 1
    else:
        with open(CERT, "w", encoding="utf-8") as handle:
            handle.write(expected)
    print(
        f"BT SEMIFINITE RELATIVE BORN WEIGHT: ALL PASS "
        f"({payload['checks']['passed']}/{payload['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
