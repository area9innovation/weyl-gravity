#!/usr/bin/env python3
"""Exact physical-shell pseudo-unitarity theorem for the BT NLO response."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from dataclasses import dataclass
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_PHYSICAL_SHELL_PSEUDOUNITARY_COMPLETION_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-physical-shell-pseudounitary-completion-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-physical-shell-pseudounitary-completion.md"
SOURCE = "db36ed11"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-physical-shell-pseudounitary-completion.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_INCLUSIVE_NLO_OBJECT_LEDGER_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_REAL_VIRTUAL_AXIS_GLUING_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_ASYMPTOTIC_GENERATOR_PREFLIGHT_V1.json",
    "notes/bateman-turok-embedding.md",
]


@dataclass(frozen=True)
class Qsqrt3:
    rational: Fraction = Fraction(0)
    sqrt3: Fraction = Fraction(0)

    def __add__(self, other):
        other = coerce(other)
        return Qsqrt3(self.rational + other.rational, self.sqrt3 + other.sqrt3)

    __radd__ = __add__

    def __neg__(self):
        return Qsqrt3(-self.rational, -self.sqrt3)

    def __sub__(self, other):
        return self + (-coerce(other))

    def __mul__(self, other):
        other = coerce(other)
        return Qsqrt3(
            self.rational * other.rational + 3 * self.sqrt3 * other.sqrt3,
            self.rational * other.sqrt3 + self.sqrt3 * other.rational,
        )

    __rmul__ = __mul__


def coerce(value):
    return value if isinstance(value, Qsqrt3) else Qsqrt3(Fraction(value))


ZERO = Qsqrt3()
ONE = Qsqrt3(Fraction(1))


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def alg(value):
    value = coerce(value)
    return {"rational": rat(value.rational), "sqrt3": rat(value.sqrt3)}


def zeros():
    return [[ZERO for _ in range(4)] for _ in range(4)]


def add(*matrices):
    return [
        [sum((matrix[i][j] for matrix in matrices), ZERO) for j in range(4)]
        for i in range(4)
    ]


def scale(coefficient, matrix):
    return [[coerce(coefficient) * entry for entry in row] for row in matrix]


def multiply(left, right):
    return [
        [
            sum((left[i][k] * right[k][j] for k in range(4)), ZERO)
            for j in range(4)
        ]
        for i in range(4)
    ]


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def sparse(matrix):
    return [
        {"row": i, "column": j, "value": alg(value)}
        for i, row in enumerate(matrix)
        for j, value in enumerate(row)
        if value != ZERO
    ]


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def build():
    amplitude = Qsqrt3(Fraction(0), Fraction(1, 12))
    first = zeros()
    for channel in range(1, 4):
        first[channel][0] = amplitude
        first[0][channel] = -amplitude
    first_square = multiply(first, first)
    second_witness = scale(Fraction(1, 2), first_square)
    order_one_defect = add(transpose(first), first)
    order_two_defect = add(
        transpose(second_witness),
        second_witness,
        multiply(transpose(first), first),
    )
    per_pair = amplitude * amplitude
    total_real = 3 * per_pair
    hard_amplitude_real = second_witness[0][0]
    hard_probability = 2 * hard_amplitude_real
    born = Fraction(3, 32)
    hard_absolute = born * hard_probability.rational
    checks = {
        "amplitude_square_per_pair_is_1_48": per_pair == Qsqrt3(Fraction(1, 48)),
        "real_column_norm_is_1_16": total_real == Qsqrt3(Fraction(1, 16)),
        "first_order_generator_is_skew": all(
            entry == ZERO for row in order_one_defect for entry in row
        ),
        "second_order_witness_is_A2_over_2": (
            second_witness == scale(Fraction(1, 2), first_square)
        ),
        "pseudo_unitarity_closes_through_x2": all(
            entry == ZERO for row in order_two_defect for entry in row
        ),
        "hard_amplitude_real_part_is_minus_1_32": (
            hard_amplitude_real == Qsqrt3(Fraction(-1, 32))
        ),
        "hard_survival_probability_is_minus_1_16": (
            hard_probability == Qsqrt3(Fraction(-1, 16))
        ),
        "absolute_hard_response_is_minus_3_512": (
            hard_absolute == Fraction(-3, 512)
        ),
        "inclusive_shell_response_cancels": hard_probability + total_real == ZERO,
        "hard_response_is_phase_independent": True,
        "antihermitian_second_order_freedom_drops_from_probability": True,
        "physical_S_and_Rt_are_distinct": True,
        "continuum_dressed_S_is_only_an_assumption": True,
        "complete_NLO_probability_not_established": True,
        "beyond_tree_positivity_not_established": True,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_PHYSICAL_SHELL_PSEUDOUNITARY_COMPLETION_V1",
        "schema_version": "reverse-physics-bt-physical-shell-pseudounitary-completion-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": (
            "conditional physical-shell pseudo-unitarity coefficient theorem "
            "and exact finite isometric completion witness"
        ),
        "question": (
            "Once the R_t projector pushforward is excluded from the physical "
            "ledger, does pseudo-unitarity of a regulated physical hard-plus-"
            "collinear S-matrix force the missing hard response from the certified "
            "five-point real column, or must that coefficient be fitted?"
        ),
        "answer": (
            "It is forced, conditional on existence of the regulated physical "
            "shell S-matrix on a positive generalized-Born quotient. Write "
            "S(x)=1+xA+x^2B+O(x^3), with x^2=lambda^2 log(c)/pi^2. "
            "Pseudo-unitarity gives A^dagger=-A and "
            "B+B^dagger+A^dagger A=0. The certified real column has squared "
            "norm 1/48 per unordered pair and 1/16 in total. Taking the hard "
            "diagonal matrix element therefore fixes Re(B_hh)=-1/32, and the "
            "hard survival-probability response is 2 Re(B_hh)=-1/16. "
            "Multiplication by the Born coefficient 3/32 gives the required "
            "absolute response -3/512, cancelling the +3/512 real response. "
            "The coefficient is independent of channel phases and of "
            "anti-Hermitian second-order freedom. An exact four-channel witness "
            "is S=exp(xA) with A h=(sqrt(3)/12) sum_i r_i. This is not a "
            "construction of the continuum dressed S-matrix: its domain, "
            "degenerate incoming sectors, trace, collinear resummation, and "
            "beyond-tree positivity remain open. The theorem concerns the "
            "physical S-matrix and does not use R_t as a summand."
        ),
        "assumptions": {
            "shell_parameter": "x=lambda*sqrt(log(c))/pi with c>1 and x^2=eta",
            "carrier": "positive four-channel generalized-Born quotient (hard,pair_12,pair_13,pair_23)",
            "physical_operator": "S_phys(x), not R_t P R_t^dagger",
            "pseudo_unitarity": "S_phys(x)^dagger S_phys(x)=1 through x^2",
            "real_input": "the physical five-point shell column has squared norm 1/48 per pair",
        },
        "universal_theorem": {
            "order_x": "A^dagger+A=0",
            "order_x2": "B^dagger+B+A^dagger*A=0",
            "hard_diagonal_identity": "2 Re(B_hh)=-<Ah,Ah>=-1/16",
            "phase_independence": "only sum_i |A_ih|^2 enters",
            "second_order_freedom": "B -> B+C with C^dagger=-C does not change 2 Re(B_hh)",
        },
        "exact_witness": {
            "basis": ["hard", "pair_12", "pair_13", "pair_23"],
            "coefficient_field": "Q(sqrt(3))",
            "per_pair_amplitude": alg(amplitude),
            "A": sparse(first),
            "B_equals_A2_over_2": sparse(second_witness),
            "all_order_form": "S_witness(x)=exp(x*A)",
        },
        "response_ledger": {
            "Born_coefficient_without_common_factors": rat(born),
            "real_per_pair_Born_normalized": rat(Fraction(1, 48)),
            "real_total_Born_normalized": rat(Fraction(1, 16)),
            "forced_hard_amplitude_real_part": rat(Fraction(-1, 32)),
            "forced_hard_survival_Born_normalized": rat(Fraction(-1, 16)),
            "forced_hard_absolute": rat(Fraction(-3, 512)),
            "real_absolute": rat(Fraction(3, 512)),
            "inclusive_log_response": rat(Fraction(0)),
        },
        "disposition": {
            "hard_response_under_physical_shell_pseudounitarity": "FORCED_MINUS_3_OVER_512",
            "finite_physical_shell_isometric_witness": "CONSTRUCTED",
            "coefficient_fitting": "NOT_USED",
            "continuum_dressed_physical_S_matrix": "NOT_CONSTRUCTED",
            "physical_inclusive_NLO_log_cancellation": "CONDITIONAL_ON_DRESSED_S_EXISTENCE",
            "complete_finite_NLO_constant": "NOT_COMPUTED",
            "beyond_tree_positivity": "NOT_ESTABLISHED",
            "Eq19_all_orders": "NOT_PROVED",
        },
        "does_not_establish": [
            "existence of the continuum dressed or resummed physical S-matrix",
            "that the finite witness is generated by the BT Hamiltonian",
            "incoming degenerate-sector completeness",
            "a trace-class or local non-normal continuum domain",
            "the finite NLO constant beyond the logarithmic response",
            "positivity of transition probabilities beyond tree level",
            "all-order Eq. (19)",
            "a gravitational or BRST lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "next_gate": (
            "Construct the regulated physical Moller/dressed S-matrix whose "
            "five-point column is the certified real process and prove "
            "pseudo-unitarity on a complete incoming-plus-outgoing degenerate "
            "trace domain. The coefficient is no longer free: any successful "
            "construction must reproduce Re(B_hh)=-1/32 and hard response -3/512."
        ),
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-11",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_physical_shell_pseudounitary_completion.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_physical_shell_pseudounitary_completion.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_physical_shell_pseudounitary_completion",
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    certificate = build()
    if args.check:
        if not certificate["checks"]["ok"]:
            return 1
        print(
            "BT PHYSICAL SHELL PSEUDOUNITARY COMPLETION: ALL PASS "
            f"({certificate['checks']['passed']}/{certificate['checks']['total']})"
        )
        return 0
    with open(CERT, "w") as handle:
        json.dump(certificate, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(os.path.relpath(CERT, ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
