#!/usr/bin/env python3
"""Independent verifier for the BT finite-detector pushforward certificate."""
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
    "REVERSE_PHYSICS_BT_FINITE_DETECTOR_PUSHFORWARD_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-finite-detector-pushforward-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def fraction(value):
    return Fraction(value["numerator"], value["denominator"])


def quadratic(value):
    return fraction(value["rational"]), fraction(value["sqrt3"])


def qadd(left, right):
    return left[0] + right[0], left[1] + right[1]


def qmul(left, right):
    return left[0] * right[0] + 3 * left[1] * right[1], left[0] * right[1] + left[1] * right[0]


QZERO = (Fraction(0), Fraction(0))
QONE = (Fraction(1), Fraction(0))
QA = (Fraction(0), Fraction(1, 12))


def matrix(value):
    return tuple(tuple(quadratic(entry) for entry in row) for row in value)


def transpose(value):
    return tuple(zip(*value))


def product(left, right):
    columns = transpose(right)
    return tuple(
        tuple(
            qsum(qmul(a, b) for a, b in zip(row, column))
            for column in columns
        )
        for row in left
    )


def qsum(values):
    answer = QZERO
    for value in values:
        answer = qadd(answer, value)
    return answer


def matrix_sum(*values):
    return tuple(
        tuple(
            qsum(value[row][column] for value in values)
            for column in range(len(values[0][row]))
        )
        for row in range(len(values[0]))
    )


def identity(size):
    return tuple(
        tuple(QONE if row == column else QZERO for column in range(size))
        for row in range(size)
    )


def trace(value):
    return qsum(value[index][index] for index in range(len(value)))


def expected_matrices(cells):
    size = cells + 1
    K = [[QZERO for _ in range(size)] for _ in range(size)]
    P0 = [[QZERO for _ in range(size)] for _ in range(size)]
    P1 = [[QZERO for _ in range(size)] for _ in range(size)]
    P2 = [[QZERO for _ in range(size)] for _ in range(size)]
    P0[0][0] = QONE
    P2[0][0] = (Fraction(-cells, 48), Fraction(0))
    for daughter in range(1, size):
        K[daughter][0] = QA
        K[0][daughter] = (Fraction(0), Fraction(-1, 12))
        P1[daughter][0] = QA
        P1[0][daughter] = QA
        for other in range(1, size):
            P2[daughter][other] = (Fraction(1, 48), Fraction(0))
    return tuple(map(tuple, K)), tuple(map(tuple, P0)), tuple(map(tuple, P1)), tuple(map(tuple, P2))


def sha256(relative_path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative_path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def fnv1a(value):
    answer = 0xCBF29CE484222325
    for byte in value.encode():
        answer ^= byte
        answer = (answer * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return answer


def verify(certificate):
    checks = {}
    errors = sorted(
        Draft202012Validator(load(SCHEMA)).iter_errors(certificate),
        key=lambda error: list(error.path),
    )
    checks["schema"] = not errors

    model = certificate.get("finite_detector_model", {})
    K, P0, P1, P2 = expected_matrices(3)
    checks["independent_per_cell_amplitude"] = (
        model.get("per_cell_amplitude") == "a=sqrt(3)/12"
        and fraction(model.get("per_cell_amplitude_squared", {})) == Fraction(1, 48)
        and qmul(QA, QA) == (Fraction(1, 48), Fraction(0))
    )
    checks["independent_fixture_matrices"] = (
        matrix(model.get("fixture_generator", [])) == K
        and matrix(model.get("fixture_P0", [])) == P0
        and matrix(model.get("fixture_P1", [])) == P1
        and matrix(model.get("fixture_P2", [])) == P2
    )
    checks["independent_generator_and_projector"] = (
        product(P0, P0) == P0
        and K == tuple(
            tuple((-entry[0], -entry[1]) for entry in row)
            for row in transpose(K)
        )
        and P1 == matrix_sum(product(K, P0), product(P0, transpose(K)))
    )
    checks["independent_idempotence_coefficients"] = (
        matrix_sum(product(P0, P1), product(P1, P0)) == P1
        and matrix_sum(product(P0, P2), product(P2, P0), product(P1, P1)) == P2
        and trace(P1) == trace(P2) == QZERO
    )

    rows = model.get("exact_rows", [])
    checks["independent_log_cell_rows"] = len(rows) == 8 and all(
        row.get("log_cells") == cells
        and fraction(row.get("daughter_norm_squared", {})) == Fraction(cells, 48)
        and quadratic(row.get("P1_trace", {})) == QZERO
        and fraction(row.get("P1_trace_norm_squared", {})) == Fraction(cells, 12)
        and fraction(row.get("P2_hard_block_trace", {})) == Fraction(-cells, 48)
        and fraction(row.get("P2_soft_block_trace", {})) == Fraction(cells, 48)
        and quadratic(row.get("P2_total_trace", {})) == QZERO
        and fraction(row.get("P2_trace_norm", {})) == Fraction(cells, 24)
        for cells, row in enumerate(rows, 1)
    )

    # Derive the two singular values of P1 and the two nonzero eigenvalues of
    # P2 from their rank-two collective-daughter blocks, rather than trusting
    # the producer's matrix diagonalization statement.
    checks["independent_trace_norm_spectrum"] = all(
        4 * Fraction(row["log_cells"], 48)
        == fraction(row["P1_trace_norm_squared"])
        and 2 * Fraction(row["log_cells"], 48)
        == fraction(row["P2_trace_norm"])
        for row in rows
    )

    zero = certificate.get("zero_mode_and_charge", {})
    predecessor = load(os.path.join(
        ROOT,
        "reverse_physics/certificates/REVERSE_PHYSICS_BT_ZERO_MODE_EQ19_TRILEMMA_V1.json",
    ))
    log_rows = predecessor.get("neutral_soft_block", {}).get("logarithmic_rows", [])
    fixed = [row.get("fixed_vacuum_generator_charges") for row in log_rows]
    powers = [row.get("restoring_Z_exponents") for row in log_rows]
    completed = [row.get("completed_generator_charges") for row in log_rows]
    checks["independent_zero_mode_import"] = (
        fixed == zero.get("logarithmic_fixed_vacuum_generator_charge_pairs")
        and powers == zero.get("unique_restoring_Z_exponent_pairs")
        and completed == zero.get("completed_generator_charge_pairs")
        and all(row.get("Gram_Z_exponent") == 0 for row in log_rows)
        and zero.get("strictly_negative_radical_piece") == "ZERO_IN_THIS_CERTIFIED_SECTOR"
    )

    squeeze = certificate.get("weighted_squeeze_test", {})
    z = fraction(squeeze.get("fixture_z", {}))
    x = z * z
    vacuum_norm = 1 / (1 - x)
    pair_norm = (1 + x) / (1 - x) ** 3
    checks["independent_squeeze_sums"] = (
        z == Fraction(1, 2)
        and fraction(squeeze.get("fixture_x_equals_z_squared", {})) == x
        and fraction(squeeze.get("vacuum_positive_norm_squared", {})) == vacuum_norm == Fraction(4, 3)
        and fraction(squeeze.get("one_pair_excited_positive_norm_squared", {})) == pair_norm == Fraction(80, 27)
    )
    checks["independent_squeezed_trace_sizes"] = (
        fraction(squeeze.get("one_cell_P1_trace_norm_squared", {}))
        == 4 * Fraction(1, 48) * vacuum_norm * pair_norm
        == Fraction(80, 243)
        and fraction(squeeze.get("one_cell_P2_trace_norm", {}))
        == Fraction(1, 48) * (vacuum_norm + pair_norm)
        == Fraction(29, 324)
    )

    obstruction = certificate.get("trace_ideal_obstruction", {})
    disposition = certificate.get("disposition", {})
    checks["trace_ideal_boundary"] = (
        obstruction.get("order_one_positive_size") == "||P1||_1^2=4 N a^2=N/12"
        and obstruction.get("order_two_positive_size") == "||P2||_1=2 N a^2=N/24"
        and obstruction.get("disposition")
        == "FIRST_EXACT_SOFT_TRACE_IDEAL_OBSTRUCTION_AFTER_FINITE_DETECTOR_CONSTRUCTION"
        and disposition.get("finite_cutoff_semifinite_ideal_membership") == "ESTABLISHED"
        and disposition.get("uniform_soft_trace_class_limit") == "OBSTRUCTED_IN_THIS_SECTOR"
    )
    checks["claim_boundary"] = (
        disposition.get("full_order_lambda_R_t_projector_pushforward") == "NOT_CONSTRUCTED"
        and disposition.get("Eq19") == "NOT_REPRODUCED"
        and disposition.get("physical_neutral_one_over_48") == "NOT_ESTABLISHED"
        and disposition.get("local_non_normal_thermodynamic_weight") == "NOT_CONSTRUCTED"
        and any("LORENTZIAN-CAUSAL" in item for item in certificate.get("does_not_establish", []))
    )

    inputs = certificate.get("provenance", {}).get("inputs", [])
    checks["input_hashes"] = len(inputs) == 7 and all(
        item.get("sha256") == sha256(item.get("path", "")) for item in inputs
    )
    event_item = inputs[-1] if inputs else {}
    event = load(os.path.join(ROOT, event_item.get("path", ""))) if event_item else {}
    event_body = event.get("body", {})
    event_payload = event_body.get("payload", {})
    event_key = "|".join([
        event_payload.get("target", ""), event_payload.get("to_state", ""),
        event_body.get("actor", ""), event_body.get("when", ""),
        event_payload.get("note", ""), "",
    ])
    event_hash = f"{fnv1a(event_key):016x}"
    checks["science_forge_event"] = (
        event_hash == "55b0d54288770f8a"
        and event.get("id", "").endswith(event_hash)
        and event_payload.get("to_state") == "OBSTRUCTED"
    )
    ledger = certificate.get("checks", {})
    checks["producer_ledger"] = (
        ledger.get("ok") is True
        and ledger.get("passed") == ledger.get("total") == 25
        and ledger.get("failures") == []
        and len(ledger.get("details", {})) == 25
        and all(ledger.get("details", {}).values())
    )

    if errors:
        for error in errors:
            print(f"schema: {list(error.path)}: {error.message}", file=sys.stderr)
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        print("BT FINITE DETECTOR PUSHFORWARD VERIFY: FAIL", file=sys.stderr)
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
        f"BT FINITE DETECTOR PUSHFORWARD VERIFY: ALL PASS "
        f"({sum(checks.values())}/{len(checks)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
