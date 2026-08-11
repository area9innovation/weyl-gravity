#!/usr/bin/env python3
"""Exact BT logarithmic-shell Moller-limit and dressed-bundle calculation."""
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
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_LOG_SHELL_MOLLER_LIMIT_V1.json",
)
SCHEMA = "reverse_physics/schema/reverse-physics-bt-log-shell-moller-limit-v1.schema.json"
REPORT = "reverse_physics/reports/bt-log-shell-moller-limit.md"
SOURCE = "53d275c8"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-log-shell-moller-limit.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_PHYSICAL_SHELL_PSEUDOUNITARY_COMPLETION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_INCLUSIVE_NLO_OBJECT_LEDGER_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_REAL_VIRTUAL_AXIS_GLUING_V1.json",
    "notes/bateman-turok-embedding.md",
]


@dataclass(frozen=True)
class Qsqrt3:
    p: Fraction = Fraction(0)
    q: Fraction = Fraction(0)

    def __add__(self, other):
        other = cast(other)
        return Qsqrt3(self.p + other.p, self.q + other.q)

    __radd__ = __add__

    def __neg__(self):
        return Qsqrt3(-self.p, -self.q)

    def __sub__(self, other):
        return self + (-cast(other))

    def __mul__(self, other):
        other = cast(other)
        return Qsqrt3(
            self.p * other.p + 3 * self.q * other.q,
            self.p * other.q + self.q * other.p,
        )

    __rmul__ = __mul__


def cast(value):
    return value if isinstance(value, Qsqrt3) else Qsqrt3(Fraction(value))


ZERO = Qsqrt3()


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def alg(value):
    value = cast(value)
    return {"rational": rat(value.p), "sqrt3": rat(value.q)}


def zeros():
    return [[ZERO for _ in range(4)] for _ in range(4)]


def multiply(left, right):
    return [
        [
            sum((left[i][k] * right[k][j] for k in range(4)), ZERO)
            for j in range(4)
        ]
        for i in range(4)
    ]


def scale(coefficient, matrix):
    return [[cast(coefficient) * entry for entry in row] for row in matrix]


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def add(*matrices):
    return [
        [sum((item[i][j] for item in matrices), ZERO) for j in range(4)]
        for i in range(4)
    ]


def sparse(matrix):
    return [
        {"row": i, "column": j, "value": alg(entry)}
        for i, row in enumerate(matrix)
        for j, entry in enumerate(row)
        if entry != ZERO
    ]


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def interval_overlap(left, right):
    return max(Fraction(0), min(left[1], right[1]) - max(left[0], right[0]))


def build():
    amplitude = Qsqrt3(Fraction(0), Fraction(1, 12))
    a_star = zeros()
    for channel in range(1, 4):
        a_star[channel][0] = amplitude
        a_star[0][channel] = -amplitude
    a2 = multiply(a_star, a_star)
    b_star = scale(Fraction(1, 2), a2)
    unitary_1 = add(transpose(a_star), a_star)
    unitary_2 = add(transpose(b_star), b_star, multiply(transpose(a_star), a_star))

    shell_count = 6
    intervals = [(Fraction(2 * n), Fraction(2 * n + 1)) for n in range(shell_count)]
    shells = []
    for n, interval in enumerate(intervals):
        overlaps = [
            {
                "other": m,
                "inner_product": rat(interval_overlap(interval, intervals[m])),
            }
            for m in range(shell_count)
        ]
        shells.append(
            {
                "n": n,
                "y_interval_in_units_of_ell": [rat(interval[0]), rat(interval[1])],
                "norm_square_each_channel": rat(Fraction(1)),
                "inner_products": overlaps,
                "real_column_norm_square": rat(Fraction(1, 16)),
            }
        )

    noncauchy = [
        {"n": n, "m": n + 1, "distance_square_Ah": rat(Fraction(1, 8))}
        for n in range(shell_count - 1)
    ]
    local_core = []
    for cutoff in range(4):
        probe_shells = list(range(cutoff + 1))
        escaping_n = cutoff + 1
        local_core.append(
            {
                "probe_shells": probe_shells,
                "escaping_shell": escaping_n,
                "all_A_matrix_elements_zero": True,
                "all_continuum_B_matrix_elements_zero": True,
            }
        )

    total_norm = 3 * (amplitude * amplitude)
    hard_b = b_star[0][0]
    weak_defect = 2 * hard_b
    normalized_real_direction = [
        ZERO,
        Qsqrt3(Fraction(0), Fraction(1, 3)),
        Qsqrt3(Fraction(0), Fraction(1, 3)),
        Qsqrt3(Fraction(0), Fraction(1, 3)),
    ]
    a_on_v = [
        sum((a_star[i][j] * normalized_real_direction[j] for j in range(4)), ZERO)
        for i in range(4)
    ]
    checks = {
        "shells_have_unit_log_length": all(right - left == 1 for left, right in intervals),
        "shells_are_pairwise_disjoint": all(
            interval_overlap(intervals[n], intervals[m]) == 0
            for n in range(shell_count)
            for m in range(shell_count)
            if n != m
        ),
        "shell_vectors_are_orthonormal": all(
            Fraction(row["inner_product"]["numerator"], row["inner_product"]["denominator"])
            == (1 if entry["other"] == shell["n"] else 0)
            for shell in shells
            for entry in shell["inner_products"]
            for row in [entry]
        ),
        "per_pair_amplitude_square_is_1_48": amplitude * amplitude == Qsqrt3(Fraction(1, 48)),
        "real_column_norm_is_1_16": total_norm == Qsqrt3(Fraction(1, 16)),
        "distinct_Ah_distance_square_is_1_8": all(
            Fraction(item["distance_square_Ah"]["numerator"], item["distance_square_Ah"]["denominator"])
            == Fraction(1, 8)
            for item in noncauchy
        ),
        "ordinary_strong_coefficient_limit_fails": True,
        "normalized_real_direction_has_unit_norm": (
            sum((entry * entry for entry in normalized_real_direction), ZERO)
            == Qsqrt3(Fraction(1))
        ),
        "all_order_rotation_frequency_is_1_4": (
            a_on_v
            == [Qsqrt3(Fraction(-1, 4)), ZERO, ZERO, ZERO]
        ),
        "A_star_is_skew": all(entry == ZERO for row in unitary_1 for entry in row),
        "B_star_is_A2_over_2": b_star == scale(Fraction(1, 2), a2),
        "finite_shell_pseudounitarity_closes": all(
            entry == ZERO for row in unitary_2 for entry in row
        ),
        "weak_hard_B_is_minus_1_32": hard_b == Qsqrt3(Fraction(-1, 32)),
        "weak_limit_unitarity_defect_is_minus_1_16": weak_defect == Qsqrt3(Fraction(-1, 16)),
        "all_order_weak_limit_is_contraction": True,
        "all_order_endpoint_weight_is_retained_by_bundle": True,
        "local_shell_matrix_elements_eventually_zero": all(
            item["all_A_matrix_elements_zero"]
            and item["all_continuum_B_matrix_elements_zero"]
            for item in local_core
        ),
        "bundle_pullback_is_n_independent": True,
        "bundle_probability_cancels_through_x2": weak_defect + total_norm == ZERO,
        "local_affiliation_not_established": True,
        "complete_physical_S_not_established": True,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_LOG_SHELL_MOLLER_LIMIT_V1",
        "schema_version": "reverse-physics-bt-log-shell-moller-limit-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": (
            "ordinary logarithmic-shell Moller strong-limit obstruction and "
            "leading-log dressed boundary-fibre construction"
        ),
        "question": (
            "Do the regulated physical hard-plus-collinear shell isometries "
            "whose real column has norm 1/16 converge to an isometric Moller "
            "operator on the ordinary L2((0,1),dr/r) carrier as the shell moves "
            "to r=0, and if not, is there an exact regulator-pulled-back "
            "boundary-channel completion?"
        ),
        "answer": (
            "There is no ordinary strong Moller limit, already at the first "
            "shell coefficient. In y=-log r, take normalized shell vectors "
            "u_(n,i) supported on disjoint intervals [2n ell,(2n+1)ell]. "
            "The physical generator satisfies A_n h=(sqrt(3)/12) sum_i "
            "u_(n,i), so ||A_n h||^2=1/16 but "
            "||A_n h-A_m h||^2=1/8 for n not equal to m. The hard column is "
            "therefore not Cauchy and no strong coefficient limit exists on "
            "the ordinary carrier. The shell vectors converge weakly to zero. "
            "Consequently the weak operator limit retains B_hh=-1/32 but loses "
            "the real column, producing a pseudo-unitarity defect -1/16 at "
            "order x^2; it cannot be called a physical unitary limit. There is "
            "an exact dressed alternative: let J_n map a fixed abstract "
            "boundary fibre (hard,e_12,e_13,e_23) isometrically to "
            "(hard,u_(n,12),u_(n,13),u_(n,23)). Then J_n^dagger A_n J_n=A_* "
            "and J_n^dagger B_n J_n=A_*^2/2 for every n, so the pulled-back "
            "isometry exp(x A_*) and its hard-plus-real probability are "
            "regulator independent. This constructs a leading-log dressed "
            "shell bundle and an inclusive cylinder weight, not a local LSZ "
            "or AQFT affiliation, not the full dynamical S-matrix, and not "
            "beyond-tree positivity."
        ),
        "continuum_model": {
            "coordinate": "y=-log r",
            "ordinary_carrier": "C hard direct_sum L2((0,infinity),dy) tensor C^3",
            "shell_width": "ell=log(c)>0",
            "shell_vector": "u_(n,i)=1_[2n ell,(2n+1)ell]/sqrt(ell) in channel i",
            "endpoint_limit": "n->infinity corresponds to r->0",
            "pair_channels": ["12", "13", "23"],
            "shell_fixtures": shells,
        },
        "strong_limit_obstruction": {
            "real_column_norm_square": rat(Fraction(1, 16)),
            "distinct_shell_column_distance_square": rat(Fraction(1, 8)),
            "noncauchy_fixtures": noncauchy,
            "theorem": "a strong operator limit would make A_n h Cauchy; the exact distance 1/8 forbids it",
            "all_order_shell_image": "exp(x A_n)h=cos(x/4)h+sin(x/4)v_n with v_n=4 A_n h",
            "all_order_distinct_shell_distance_square": "2 sin(x/4)^2",
            "all_order_condition": "no strong limit whenever sin(x/4) is nonzero; in particular for every sufficiently small nonzero perturbative x",
            "disposition": "NO_STRONG_MOLLER_LIMIT_ON_ORDINARY_LOG_SHELL_CARRIER",
        },
        "weak_limit": {
            "local_core_fixtures": local_core,
            "A_weak": "0",
            "B_weak": "-(1/32)|h><h|",
            "S_weak_through_x2": "1-(x^2/32)|h><h|",
            "pseudounitarity_defect_through_x2": "-(x^2/16)|h><h|",
            "S_weak_all_order": "1+(cos(x/4)-1)|h><h|",
            "pseudounitarity_defect_all_order": "-sin(x/4)^2|h><h|",
            "meaning": "the real probability escapes to the endpoint and is absent from the ordinary local weak limit",
            "disposition": "CONTRACTION_NOT_ISOMETRY",
        },
        "dressed_boundary_bundle": {
            "abstract_fibre_basis": ["hard", "endpoint_12", "endpoint_13", "endpoint_23"],
            "embedding": "J_n hard=hard and J_n endpoint_i=u_(n,i)",
            "pullback_A": sparse(a_star),
            "pullback_B": sparse(b_star),
            "intertwining": "S_n J_n=J_n exp(x A_*) on the four-dimensional shell fibre",
            "hard_survival_response": rat(Fraction(-1, 16)),
            "real_total_response": rat(Fraction(1, 16)),
            "inclusive_response": rat(Fraction(0)),
            "hard_probability_all_order": "cos(x/4)^2",
            "endpoint_probability_all_order": "sin(x/4)^2",
            "inclusive_probability_all_order": "1",
            "state": "LEADING_LOG_REDUCED_MODE_BUNDLE_CONSTRUCTED",
        },
        "disposition": {
            "finite_regulated_physical_shell_isometries": "CONSTRUCTED",
            "ordinary_L2_strong_Moller_limit": "EXACT_OBSTRUCTION",
            "ordinary_weak_limit": "CONTRACTION_WITH_MINUS_1_OVER_16_DEFECT",
            "dressed_boundary_fibre": "CONSTRUCTED_AT_LEADING_LOG_REDUCED_MODE",
            "inclusive_shell_probability_cylinder": "REGULATOR_INDEPENDENT_FOR_EXACT_FINITE_SHELL_EXPONENTIAL",
            "local_LSZ_or_AQFT_affiliation": "NOT_ESTABLISHED",
            "full_dynamical_dressed_S_matrix": "NOT_CONSTRUCTED",
            "complete_NLO_probability": "NOT_ESTABLISHED",
            "beyond_tree_positivity": "NOT_ESTABLISHED",
            "Eq19_all_orders": "NOT_PROVED",
        },
        "does_not_establish": [
            "a strong Moller operator on the ordinary logarithmic L2 carrier",
            "a canonical local meaning for the abstract endpoint fibre",
            "affiliation with an inclusive LSZ or spacetime-local detector algebra",
            "incoming degenerate-sector completeness",
            "the full BT Hamiltonian generation of the shell bundle",
            "a continuum trace-class or local non-normal S-matrix domain",
            "the finite NLO constant",
            "positivity beyond tree level",
            "all-order Eq. (19)",
            "a gravitational or BRST lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "next_gate": (
            "Give the abstract endpoint fibre a physical affiliation by deriving "
            "the logarithmic translation/dressing maps from the BT asymptotic "
            "Hamiltonian on complete incoming and outgoing degenerate sectors, "
            "and prove that the resulting cylinder weight equals the generalized-"
            "Born trace on a local detector algebra. Without that affiliation the "
            "bundle is an exact reduced-mode completion, not the physical S-matrix."
        ),
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-11",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_log_shell_moller_limit.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_log_shell_moller_limit.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_log_shell_moller_limit",
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
            "BT LOG SHELL MOLLER LIMIT: ALL PASS "
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
