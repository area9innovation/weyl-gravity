#!/usr/bin/env python3
"""Independent verifier for the BT semifinite relative Born-weight certificate."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SEMIFINITE_RELATIVE_BORN_WEIGHT_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-semifinite-relative-born-weight-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def fraction(value):
    return Fraction(value["numerator"], value["denominator"])


def matrix(value):
    return tuple(tuple(fraction(entry) for entry in row) for row in value)


def transpose(value):
    return tuple(zip(*value))


def product(left, right):
    columns = transpose(right)
    return tuple(
        tuple(sum((a * b for a, b in zip(row, column)), Fraction(0)) for column in columns)
        for row in left
    )


def matrix_sum(values):
    values = list(values)
    answer = [[Fraction(0) for _ in values[0][0]] for _ in values[0]]
    for value in values:
        for row in range(len(value)):
            for column in range(len(value[row])):
                answer[row][column] += value[row][column]
    return tuple(tuple(row) for row in answer)


def identity(size):
    return tuple(
        tuple(Fraction(int(row == column)) for column in range(size))
        for row in range(size)
    )


def operator_trace(value):
    return sum((value[index][index] for index in range(len(value))), Fraction(0))


def adjoint(value, fundamental_symmetry):
    return product(product(fundamental_symmetry, transpose(value)), fundamental_symmetry)


def sha256(relative_path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative_path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(certificate):
    checks = {}

    errors = sorted(
        Draft202012Validator(load(SCHEMA)).iter_errors(certificate),
        key=lambda error: list(error.path),
    )
    checks["schema"] = not errors

    orbit = certificate.get("semifinite_orbit_trace", {})
    windows = orbit.get("orbit_windows", [])
    checks["semifinite_window_arithmetic"] = len(windows) == 9 and all(
        row.get("cutoff") == cutoff
        and fraction(row.get("finite_projection_trace", {})) == 2 * cutoff + 1
        and fraction(row.get("relative_identity_weight", {})) == 1
        and fraction(row.get("relative_central_cell_weight", {}))
        == Fraction(1, 2 * cutoff + 1)
        and fraction(row.get("sum_of_cell_weights", {})) == 1
        for cutoff, row in enumerate(windows)
    )
    checks["semifinite_boundary"] = (
        orbit.get("localized_projection_weight") == "Tau(E_n)=1"
        and orbit.get("identity_weight") == "Tau(1)=INFINITY"
        and orbit.get("disposition") == "CONSTRUCTED"
    )

    laurent = orbit.get("laurent_window_rows", [])
    checks["laurent_coefficient_trace"] = len(laurent) == 9 and all(
        row.get("power") == power
        and fraction(row.get("normalized_window_expectation", {}))
        == int(power == 0)
        and fraction(row.get("coefficient_trace", {})) == int(power == 0)
        for power, row in zip(range(-4, 5), laurent)
    )

    relative = certificate.get("relative_detector_state", {})
    counterexample = relative.get("traciality_counterexample", {})
    # Recompute E00 E01 E10 E00 and the reversed product as matrix units.
    E00 = ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(0)))
    E01 = ((Fraction(0), Fraction(1)), (Fraction(0), Fraction(0)))
    E10 = ((Fraction(0), Fraction(0)), (Fraction(1), Fraction(0)))
    omega_xy = operator_trace(product(product(E00, product(E01, E10)), E00))
    omega_yx = operator_trace(product(product(E00, product(E10, E01)), E00))
    checks["independent_traciality_counterexample"] = (
        omega_xy == 1
        and omega_yx == 0
        and fraction(counterexample.get("omega_XY", {})) == omega_xy
        and fraction(counterexample.get("omega_YX", {})) == omega_yx
        and relative.get("status")
        == "NORMAL_STATE_FOR_EACH_FINITE_TRACE_P_BUT_NOT_A_TRACE_IN_GENERAL"
    )

    theorem = certificate.get("conditional_Born_theorem", {})
    fixture = theorem.get("rational_partition_fixture", {})
    J = matrix(fixture.get("fundamental_symmetry", []))
    S = matrix(fixture.get("cross_Krein_isometry", []))
    incoming = matrix(fixture.get("incoming_projection", []))
    outputs = [matrix(value) for value in fixture.get("output_projections", [])]
    checks["independent_cross_Krein_isometry"] = (
        product(adjoint(S, J), S) == identity(3)
        and product(J, S) == product(S, J)
    )
    checks["independent_partition"] = (
        len(outputs) == 3
        and matrix_sum(outputs) == identity(3)
        and product(incoming, incoming) == incoming
        and operator_trace(incoming) == 1
    )

    processes = [product(product(output, S), incoming) for output in outputs]
    weights = [
        operator_trace(product(adjoint(process, J), process))
        for process in processes
    ]
    recorded_weights = [fraction(value) for value in fixture.get("process_weights", [])]
    checks["independent_conditional_weights"] = (
        weights == [Fraction(9, 25), Fraction(16, 25), Fraction(0)]
        and recorded_weights == weights
        and sum(weights, Fraction(0)) == 1
        and fraction(fixture.get("weight_sum", {})) == 1
    )

    weak = theorem.get("weak_null_fixture", {})
    Jn = matrix(weak.get("fundamental_symmetry", []))
    B = matrix(weak.get("B", []))
    C = matrix(weak.get("C", []))
    A = matrix(weak.get("A_equals_B_plus_C", []))
    CdagC = operator_trace(product(adjoint(C, Jn), C))
    BdagC = operator_trace(product(adjoint(B, Jn), C))
    CdagB = operator_trace(product(adjoint(C, Jn), B))
    BdagB = operator_trace(product(adjoint(B, Jn), B))
    AdagA = operator_trace(product(adjoint(A, Jn), A))
    checks["independent_weak_null_fixture"] = (
        A == matrix_sum([B, C])
        and C != ((Fraction(0), Fraction(0)), (Fraction(0), Fraction(0)))
        and adjoint(C, Jn) == C
        and CdagC == BdagC == CdagB == 0
        and BdagB == AdagA == Fraction(18, 25)
        and fraction(weak.get("Tr_Cdagger_C", {})) == CdagC
        and fraction(weak.get("Tr_Bdagger_C", {})) == BdagC
        and fraction(weak.get("Tr_Cdagger_B", {})) == CdagB
        and fraction(weak.get("Tr_Bdagger_B", {})) == BdagB
        and fraction(weak.get("Tr_Adagger_A", {})) == AdagA
    )

    checks["theorem_boundary"] = (
        len(theorem.get("hypotheses", [])) == 5
        and theorem.get("identity_trace_requirement")
        == "NONE; Tau(1)=INFINITY is compatible with the theorem"
        and theorem.get("disposition")
        == "PROVED_ON_FINITE_DETECTOR_IDEAL_UNDER_WEAK_GHOST_HYPOTHESES"
        and "Tr(P_in)" in theorem.get("normalization_proof", "")
        and ">=0" in theorem.get("positivity_proof", "")
    )

    thermo = certificate.get("thermodynamic_boundary", {})
    disposition = certificate.get("disposition", {})
    checks["thermodynamic_fail_closed_boundary"] = (
        thermo.get("non_normal_local_state") == "NOT_CONSTRUCTED"
        and thermo.get("full_nonlinear_R_t") == "NOT_CONSTRUCTED"
        and thermo.get("Eq19") == "NOT_REPRODUCED"
        and thermo.get("physical_one_over_48") == "NOT_ESTABLISHED"
        and disposition.get("thermodynamic_normal_state") == "NOT_CONSTRUCTED"
        and disposition.get("unbounded_squeeze_trace_ideal_control")
        == "NOT_CONSTRUCTED"
        and disposition.get("physical_neutral_one_over_48")
        == "NOT_ESTABLISHED"
    )
    checks["no_go_is_preserved"] = (
        disposition.get("conditional_state_cyclicity")
        == "REFUTED_BY_EXACT_MATRIX_UNIT_WITNESS"
        and disposition.get("finite_normalized_trace_on_full_orbit_algebra")
        == "REMAINS_OBSTRUCTED"
        and any(
            "normalized corner state is cyclic" in statement
            for statement in certificate.get("does_not_establish", [])
        )
    )

    inputs = certificate.get("provenance", {}).get("inputs", [])
    checks["input_hashes"] = len(inputs) == 4 and all(
        item.get("sha256") == sha256(item.get("path", "")) for item in inputs
    )
    recorded_checks = certificate.get("checks", {})
    checks["producer_check_ledger"] = (
        recorded_checks.get("ok") is True
        and recorded_checks.get("passed") == 29
        and recorded_checks.get("total") == 29
        and recorded_checks.get("failures") == []
        and len(recorded_checks.get("details", {})) == 29
        and all(recorded_checks.get("details", {}).values())
    )

    if errors:
        for error in errors:
            print(f"schema: {list(error.path)}: {error.message}", file=sys.stderr)
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        print("BT SEMIFINITE RELATIVE BORN WEIGHT VERIFY: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return False, checks
    return True, checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args()
    ok, checks = verify(load(args.verify))
    if not ok:
        return 1
    print(
        f"BT SEMIFINITE RELATIVE BORN WEIGHT VERIFY: ALL PASS "
        f"({sum(checks.values())}/{len(checks)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
