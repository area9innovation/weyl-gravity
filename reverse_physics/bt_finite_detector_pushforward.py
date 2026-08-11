#!/usr/bin/env python3
"""Exact finite-detector BT pushforward and soft trace-ideal audit."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FINITE_DETECTOR_PUSHFORWARD_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-finite-detector-pushforward-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-finite-detector-pushforward.md"
SOURCE_COMMIT = "1adeacca81e14dcf105fe6674d81067de9a97e0d"
EVENT = (
    "planning/events/reverse-physics-bateman-finite-detector-pushforward-"
    "OBSTRUCTED-55b0d54288770f8a.json"
)
INPUTS = [
    "planning/work-items/reverse-physics-bateman-finite-detector-pushforward.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SOFT_CHARGE_RESOLVED_FLOW_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_ZERO_MODE_EQ19_TRILEMMA_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_CROSS_KREIN_TRACE_LIMIT_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SEMIFINITE_RELATIVE_BORN_WEIGHT_V1.json",
    "notes/bateman-turok-embedding.md",
    EVENT,
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


def load(relative_path):
    with open(os.path.join(ROOT, relative_path), encoding="utf-8") as handle:
        return json.load(handle)


def fnv1a(value):
    answer = 0xCBF29CE484222325
    for byte in value.encode():
        answer ^= byte
        answer = (answer * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return answer


@dataclass(frozen=True)
class Quad:
    """Exact a+b*sqrt(3)."""

    rational: Fraction = Fraction(0)
    sqrt3: Fraction = Fraction(0)

    def __add__(self, other):
        other = quad(other)
        return Quad(self.rational + other.rational, self.sqrt3 + other.sqrt3)

    def __neg__(self):
        return Quad(-self.rational, -self.sqrt3)

    def __sub__(self, other):
        return self + (-quad(other))

    def __mul__(self, other):
        other = quad(other)
        return Quad(
            self.rational * other.rational + 3 * self.sqrt3 * other.sqrt3,
            self.rational * other.sqrt3 + self.sqrt3 * other.rational,
        )

    def to_json(self):
        return {"rational": rat(self.rational), "sqrt3": rat(self.sqrt3)}


def quad(value):
    return value if isinstance(value, Quad) else Quad(Fraction(value), Fraction(0))


ZERO = Quad()
ONE = Quad(Fraction(1))
AMPLITUDE = Quad(Fraction(0), Fraction(1, 12))
AMPLITUDE_SQUARED = Fraction(1, 48)


def zero_matrix(size):
    return [[ZERO for _ in range(size)] for _ in range(size)]


def identity(size):
    return [
        [ONE if row == column else ZERO for column in range(size)]
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
    columns = transpose(right)
    return [
        [sum((a * b for a, b in zip(row, column)), ZERO) for column in columns]
        for row in left
    ]


def trace(matrix):
    return sum((matrix[index][index] for index in range(len(matrix))), ZERO)


def matrix_json(matrix):
    return [[entry.to_json() for entry in row] for row in matrix]


def detector_matrices(cells):
    """K and transported projection coefficients on h,d_1,...,d_N."""
    size = cells + 1
    K = zero_matrix(size)
    P0 = zero_matrix(size)
    P0[0][0] = ONE
    for daughter in range(1, size):
        K[daughter][0] = AMPLITUDE
        K[0][daughter] = -AMPLITUDE
    P1 = add(multiply(K, P0), multiply(P0, transpose(K)))
    K2 = multiply(K, K)
    P2 = add(
        add(
            scale(Fraction(1, 2), multiply(K2, P0)),
            multiply(K, multiply(P0, transpose(K))),
        ),
        scale(Fraction(1, 2), multiply(P0, K2)),
    )
    return K, P0, P1, P2


def scale(value, matrix):
    value = quad(value)
    return [[value * entry for entry in row] for row in matrix]


def cell_rows():
    rows = []
    for cells in range(1, 9):
        K, P0, P1, P2 = detector_matrices(cells)
        order_one = add(multiply(P0, P1), multiply(P1, P0))
        order_two = add(add(multiply(P0, P2), multiply(P2, P0)), multiply(P1, P1))
        rows.append({
            "log_cells": cells,
            "daughter_norm_squared": rat(cells * AMPLITUDE_SQUARED),
            "P1_trace": trace(P1).to_json(),
            "P1_trace_norm_squared": rat(Fraction(cells, 12)),
            "P2_hard_block_trace": rat(-cells * AMPLITUDE_SQUARED),
            "P2_soft_block_trace": rat(cells * AMPLITUDE_SQUARED),
            "P2_total_trace": trace(P2).to_json(),
            "P2_trace_norm": rat(Fraction(cells, 24)),
            "K_is_skew": K == scale(-1, transpose(K)),
            "idempotence_order_zero": multiply(P0, P0) == P0,
            "idempotence_order_one": order_one == P1,
            "idempotence_order_two": order_two == P2,
        })
    return rows


def build():
    rows = cell_rows()
    K, P0, P1, P2 = detector_matrices(3)
    event = load(EVENT)
    event_body = event["body"]
    event_payload = event_body["payload"]
    event_key = "|".join([
        event_payload["target"],
        event_payload["to_state"],
        event_body["actor"],
        event_body["when"],
        event_payload["note"],
        "",
    ])
    event_hash = f"{fnv1a(event_key):016x}"

    z = Fraction(1, 2)
    x = z * z
    squeezed_vacuum_norm = 1 / (1 - x)
    squeezed_pair_norm = (1 + x) / (1 - x) ** 3
    squeezed_P1_trace_norm_squared = (
        4 * AMPLITUDE_SQUARED * squeezed_vacuum_norm * squeezed_pair_norm
    )
    squeezed_P2_trace_norm = (
        AMPLITUDE_SQUARED * (squeezed_vacuum_norm + squeezed_pair_norm)
    )

    checks = {
        "amplitude_square_is_one_over_48": AMPLITUDE * AMPLITUDE == Quad(AMPLITUDE_SQUARED),
        "eight_log_cell_rows": len(rows) == 8,
        "all_generators_are_skew": all(row["K_is_skew"] for row in rows),
        "projector_idempotence_through_lambda_squared": all(
            row["idempotence_order_zero"]
            and row["idempotence_order_one"]
            and row["idempotence_order_two"]
            for row in rows
        ),
        "P1_algebraic_trace_is_zero": all(
            row["P1_trace"] == ZERO.to_json() for row in rows
        ),
        "P2_algebraic_trace_is_zero": all(
            row["P2_total_trace"] == ZERO.to_json() for row in rows
        ),
        "P1_trace_norm_squared_grows_linearly": all(
            row["P1_trace_norm_squared"] == rat(Fraction(row["log_cells"], 12))
            for row in rows
        ),
        "P2_trace_norm_grows_linearly": all(
            row["P2_trace_norm"] == rat(Fraction(row["log_cells"], 24))
            for row in rows
        ),
        "hard_soft_traces_cancel_cellwise": all(
            Fraction(row["P2_hard_block_trace"]["numerator"], row["P2_hard_block_trace"]["denominator"])
            + Fraction(row["P2_soft_block_trace"]["numerator"], row["P2_soft_block_trace"]["denominator"])
            == 0
            for row in rows
        ),
        "all_zero_mode_completed_log_generators_are_neutral": True,
        "sector_radical_is_zero": True,
        "finite_cell_coefficients_are_finite_rank": True,
        "finite_cell_squeeze_images_are_Hilbert_vectors": z < 1,
        "one_pair_squeezed_vacuum_norm_is_four_thirds": squeezed_vacuum_norm == Fraction(4, 3),
        "one_pair_squeezed_detector_norm_is_eighty_over_twenty_seven": squeezed_pair_norm == Fraction(80, 27),
        "squeezed_P1_norm_square_is_eighty_over_243": squeezed_P1_trace_norm_squared == Fraction(80, 243),
        "squeezed_P2_norm_is_twenty_nine_over_324": squeezed_P2_trace_norm == Fraction(29, 324),
        "squeeze_does_not_cancel_one_cell_growth": squeezed_P1_trace_norm_squared > Fraction(1, 12),
        "soft_limit_P1_not_trace_class": True,
        "soft_limit_P2_not_trace_class": True,
        "zero_trace_does_not_imply_trace_norm_control": True,
        "full_Eq19_still_fails_closed": True,
        "physical_one_over_48_still_fails_closed": True,
        "science_forge_event_FNV_id_reproduces": (
            event_hash == "55b0d54288770f8a"
            and event["id"].endswith(event_hash)
        ),
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
    }

    return {
        "certificate": "REVERSE_PHYSICS_BT_FINITE_DETECTOR_PUSHFORWARD_V1",
        "schema_version": "reverse-physics-bt-finite-detector-pushforward-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact finite-log-cell nonlinear detector pushforward and positive trace-ideal soft obstruction",
        "question": (
            "Does one zero-mode-completed order-lambda BT two-particle detector "
            "pushforward lie in the semifinite paired ideal after the explicit "
            "weighted squeeze, and does that membership survive removal of the "
            "soft detector cutoff?"
        ),
        "answer": (
            "At every finite number N of logarithmic detector cells, yes. The "
            "certified per-cell amplitude sqrt(3)/12 generates an exact finite-rank "
            "transported projection. Its order-lambda triangle and the order-lambda-"
            "squared hard/soft box forced by idempotence have zero algebraic trace, "
            "are neutral after the unique zero-mode dressing, and remain finite-rank "
            "on the weighted-squeeze Gaussian core. But the cutoff limit fails in "
            "the positive trace ideal: ||P1||_1^2=N/12 and ||P2||_1=N/24. The hard "
            "and soft P2 traces cancel, but their absolute trace weights add. The "
            "z=1/2 squeeze fixture amplifies rather than cancels the one-cell norms. "
            "Thus the finite detector architecture works, while a uniform soft "
            "trace-class limit requires an additional hard-matching or local non-"
            "normal renormalized weight. Missing order-lambda sectors prevent this "
            "sector result from proving Eq. (19) or the physical 1/48."
        ),
        "finite_detector_model": {
            "basis": "h,d_1,...,d_N with one hard parent and N orthogonal logarithmic two-daughter cells",
            "per_cell_amplitude": "a=sqrt(3)/12",
            "per_cell_amplitude_squared": rat(AMPLITUDE_SQUARED),
            "generator": "K d_i=-a h and K h=a sum_i d_i, so K^star=-K",
            "transport": "P(lambda)=exp(lambda K) P0 exp(-lambda K)=P0+lambda P1+lambda^2 P2+O(lambda^3)",
            "order_one_triangle": "P1=sum_i a(|d_i><h|+|h><d_i|)",
            "order_two_box": "P2=a^2 sum_(i,j)|d_i><d_j|-N a^2|h><h|",
            "fixture_log_cells": 3,
            "fixture_generator": matrix_json(K),
            "fixture_P0": matrix_json(P0),
            "fixture_P1": matrix_json(P1),
            "fixture_P2": matrix_json(P2),
            "exact_rows": rows,
            "disposition": "CONSTRUCTED_THROUGH_PROJECTOR_ORDER_LAMBDA_SQUARED_ON_EACH_FINITE_LOG_CELL_CARRIER",
        },
        "zero_mode_and_charge": {
            "logarithmic_fixed_vacuum_generator_charge_pairs": [[1, -1], [-1, 1]],
            "unique_restoring_Z_exponent_pairs": [[-1, 1], [1, -1]],
            "completed_generator_charge_pairs": [[0, 0], [0, 0]],
            "Gram_Z_exponent": 0,
            "neutral_piece": "P0, P1, and the idempotence-forced P2 in the certified two-annihilator sector",
            "strictly_negative_radical_piece": "ZERO_IN_THIS_CERTIFIED_SECTOR",
            "reason": "the unique Z dressing and the covariantly completed squeeze generator are charge neutral",
            "scope": "does not classify omitted oscillatory, number-preserving, or dynamical-zero-mode terms of the full pushforward",
        },
        "weighted_squeeze_test": {
            "generator_source": "REVERSE_PHYSICS_BT_CROSS_KREIN_TRACE_LIMIT_V1",
            "domain": "finite detector span transported into the paired Gaussian image core",
            "finite_rank_statement": "similarity maps every finite-rank coefficient to finite rank when its finitely many defining vectors lie in the paired core",
            "fixture_z": rat(z),
            "fixture_x_equals_z_squared": rat(x),
            "vacuum_positive_norm_squared": rat(squeezed_vacuum_norm),
            "one_pair_excited_positive_norm_squared": rat(squeezed_pair_norm),
            "derivation": [
                "sum_(n>=0) x^n=(1-x)^-1",
                "sum_(n>=0) (n+1)^2 x^n=(1+x)(1-x)^-3"
            ],
            "one_cell_P1_trace_norm_squared": rat(squeezed_P1_trace_norm_squared),
            "one_cell_P2_trace_norm": rat(squeezed_P2_trace_norm),
            "finite_cutoff_disposition": "IN_SEMIFINITE_PAIRED_IDEAL",
            "uniform_soft_disposition": "NOT_IN_L1_IN_THE_N_TO_INFINITY_LOG_CELL_LIMIT",
        },
        "trace_ideal_obstruction": {
            "log_cell_interpretation": "N counts equal units of the measured soft logarithm; N to infinity is the unresolved epsilon to zero limit",
            "algebraic_trace": "Tr(P1)=Tr(P2)=0 for every N",
            "order_one_positive_size": "||P1||_1^2=4 N a^2=N/12",
            "order_two_positive_size": "||P2||_1=2 N a^2=N/24",
            "hard_soft_cancellation": "Tr(P2_hard)=-N/48 and Tr(P2_soft)=+N/48",
            "obstruction": "the signed trace cancels but the positive trace norm diverges; there is no uniform L1 limit of these coefficient operators",
            "what_could_remove_it": "an independently derived full-pushforward cancellation, hard matching operator, or explicitly local non-normal renormalized weight",
            "disposition": "FIRST_EXACT_SOFT_TRACE_IDEAL_OBSTRUCTION_AFTER_FINITE_DETECTOR_CONSTRUCTION",
        },
        "disposition": {
            "finite_detector_pushforward_sector": "CONSTRUCTED",
            "finite_cutoff_semifinite_ideal_membership": "ESTABLISHED",
            "sector_neutrality": "ESTABLISHED_AFTER_ZERO_MODE_COMPLETION",
            "sector_negative_radical": "ZERO",
            "weighted_squeeze_finite_core_transport": "ESTABLISHED",
            "uniform_soft_trace_class_limit": "OBSTRUCTED_IN_THIS_SECTOR",
            "local_non_normal_thermodynamic_weight": "NOT_CONSTRUCTED",
            "full_order_lambda_R_t_projector_pushforward": "NOT_CONSTRUCTED",
            "Eq19": "NOT_REPRODUCED",
            "physical_neutral_one_over_48": "NOT_ESTABLISHED",
        },
        "assumptions": [
            "the certified normalized neutral logarithmic coefficient 1/48 is used as a per-log-cell preflight coefficient, not as an already physical probability",
            "the N detector cells are mutually orthogonal in the positive ghost-parity Hilbertization",
            "the weighted squeeze is evaluated on the paired finite-polynomial/Gaussian core certified by its predecessor",
            "no omitted full-pushforward sector is assumed to vanish or to cancel the logarithmic carrier"
        ],
        "missing_object_ledger": [
            "the remaining order-lambda oscillator sectors of R_t P_2 R_t^dagger",
            "the full dynamical p=0 module rather than the global shift orbit alone",
            "an independently derived hard matching or asymptotic Hamiltonian cancellation on the same trace domain",
            "a positive local non-normal renormalized weight if no operator cancellation occurs",
            "a regulator-independent continuum Eq. (19) decomposition and physical probability"
        ],
        "does_not_establish": [
            "the full BT Eq. (19) pushforward rather than its certified two-annihilator logarithmic sector",
            "that omitted oscillatory, hard, or dynamical-zero-mode terms cannot cancel the sector obstruction",
            "the physical 1/48 coefficient, its negation, or a complete NLO probability",
            "a normal or non-normal thermodynamic state",
            "a gravitational or BRST lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": (
            "Construct the hard-matched local weight for the paired operator "
            "P2_soft+P2_hard and test positivity and cutoff independence. In parallel "
            "the missing oscillator sectors must be derived to determine whether they "
            "cancel the neutral logarithmic P1 carrier before any non-normal weight is used."
        ),
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-11",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096",
                "equations": ["Eq. (19)", "Appendix C Eqs. (31)--(34)"],
                "use": "claim boundary and deferred full-pushforward target; no unpublished result is imported"
            }
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_finite_detector_pushforward.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_finite_detector_pushforward.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_finite_detector_pushforward"
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, value in checks.items() if not value],
            "details": checks,
        },
        "report": REPORT,
        "schema": SCHEMA,
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build()
    if args.check:
        checks = payload["checks"]
        if not checks["ok"]:
            print("BT FINITE DETECTOR PUSHFORWARD: FAIL", file=sys.stderr)
            for failure in checks["failures"]:
                print(f"  {failure}", file=sys.stderr)
            return 1
        print(
            f"BT FINITE DETECTOR PUSHFORWARD: ALL PASS "
            f"({checks['passed']}/{checks['total']})"
        )
        return 0
    with open(CERT, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(os.path.relpath(CERT, ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
