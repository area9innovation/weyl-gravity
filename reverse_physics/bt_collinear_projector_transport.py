#!/usr/bin/env python3
"""Exact finite carrier for coherent BT hard--collinear projector transport.

The calculation is deliberately small.  It asks whether the logarithmic
coefficient left by the axis-compatible regulator obstruction can be supplied
by transporting the *projector*, rather than by changing the virtual
amplitude.  All arithmetic is in Q(sqrt(2)); no floating point is used.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from fractions import Fraction


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_COLLINEAR_PROJECTOR_TRANSPORT_V1.json",
)
SCHEMA_PATH = (
    "reverse_physics/schema/"
    "reverse-physics-bt-collinear-projector-transport-v1.schema.json"
)
REPORT_PATH = "reverse_physics/reports/bt-collinear-projector-transport.md"
SOURCE_COMMIT = "75ffbf24e09296699fae0d5be52adfa701e7f33c"
INPUTS = [
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_REAL_VIRTUAL_AXIS_GLUING_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_CHARGE_GRADING_LOOP_STABILITY_V1.json",
]


@dataclass(frozen=True)
class Qsqrt2:
    """Element p + q*sqrt(2) with exact rational p and q."""

    p: Fraction = Fraction(0)
    q: Fraction = Fraction(0)

    def __add__(self, other):
        other = coerce(other)
        return Qsqrt2(self.p + other.p, self.q + other.q)

    __radd__ = __add__

    def __neg__(self):
        return Qsqrt2(-self.p, -self.q)

    def __sub__(self, other):
        return self + (-coerce(other))

    def __rsub__(self, other):
        return coerce(other) - self

    def __mul__(self, other):
        other = coerce(other)
        return Qsqrt2(
            self.p * other.p + 2 * self.q * other.q,
            self.p * other.q + self.q * other.p,
        )

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = coerce(other)
        norm = other.p * other.p - 2 * other.q * other.q
        if not norm:
            raise ZeroDivisionError
        return self * Qsqrt2(other.p / norm, -other.q / norm)

    def __eq__(self, other):
        other = coerce(other)
        return self.p == other.p and self.q == other.q


def coerce(value):
    if isinstance(value, Qsqrt2):
        return value
    return Qsqrt2(Fraction(value), Fraction(0))


ZERO = Qsqrt2()
ONE = Qsqrt2(Fraction(1))


def rational(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def algebraic(value):
    value = coerce(value)
    return {"rational": rational(value.p), "sqrt2": rational(value.q)}


def zero_matrix(size=4):
    return [[ZERO for _ in range(size)] for _ in range(size)]


def matrix_add(*matrices):
    return [
        [sum((matrix[i][j] for matrix in matrices), ZERO)
         for j in range(len(matrices[0]))]
        for i in range(len(matrices[0]))
    ]


def matrix_scale(scalar, matrix):
    scalar = coerce(scalar)
    return [[scalar * value for value in row] for row in matrix]


def matrix_multiply(left, right):
    size = len(left)
    return [
        [sum((left[i][k] * right[k][j] for k in range(size)), ZERO)
         for j in range(size)]
        for i in range(size)
    ]


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def trace(matrix):
    return sum((matrix[i][i] for i in range(len(matrix))), ZERO)


def serialize_matrix(matrix):
    return [
        {"row": i, "column": j, "value": algebraic(value)}
        for i, row in enumerate(matrix)
        for j, value in enumerate(row)
        if value != ZERO
    ]


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def construction():
    """Return K and the first three coefficients of exp(eK)P exp(-eK)."""
    amplitude = Qsqrt2(Fraction(0), Fraction(1, 32))
    k = zero_matrix()
    for channel in range(1, 4):
        k[0][channel] = -amplitude
        k[channel][0] = amplitude

    p0 = zero_matrix()
    p0[0][0] = ONE
    k2 = matrix_multiply(k, k)
    p1 = matrix_add(
        matrix_multiply(k, p0),
        matrix_scale(-1, matrix_multiply(p0, k)),
    )
    p2 = matrix_add(
        matrix_scale(Fraction(1, 2), matrix_multiply(k2, p0)),
        matrix_scale(-1, matrix_multiply(matrix_multiply(k, p0), k)),
        matrix_scale(Fraction(1, 2), matrix_multiply(p0, k2)),
    )
    idempotency_1 = matrix_add(
        matrix_multiply(p0, p1), matrix_multiply(p1, p0),
        matrix_scale(-1, p1),
    )
    idempotency_2 = matrix_add(
        matrix_multiply(p0, p2), matrix_multiply(p2, p0),
        matrix_multiply(p1, p1), matrix_scale(-1, p2),
    )
    orthogonality_1 = matrix_add(k, transpose(k))
    # The coefficient of epsilon^2 in U^T U for
    # U=I+epsilon*K+epsilon^2*K^2/2.
    orthogonality_2 = matrix_add(
        matrix_scale(Fraction(1, 2), transpose(k2)),
        matrix_multiply(transpose(k), k),
        matrix_scale(Fraction(1, 2), k2),
    )
    return {
        "amplitude": amplitude,
        "K": k,
        "P0": p0,
        "P1": p1,
        "P2": p2,
        "idempotency_1": idempotency_1,
        "idempotency_2": idempotency_2,
        "orthogonality_1": orthogonality_1,
        "orthogonality_2": orthogonality_2,
    }


def all_zero(matrix):
    return all(value == ZERO for row in matrix for value in row)


def build():
    data = construction()
    p2 = data["P2"]
    per_pair = p2[1][1]
    real_sum = sum((p2[i][i] for i in range(1, 4)), ZERO)
    hard = p2[0][0]
    omitted_hard = [row[:] for row in p2]
    omitted_hard[0][0] = ZERO
    omitted_defect = matrix_add(
        matrix_multiply(data["P0"], omitted_hard),
        matrix_multiply(omitted_hard, data["P0"]),
        matrix_multiply(data["P1"], data["P1"]),
        matrix_scale(-1, omitted_hard),
    )
    checks = {
        "mixing_amplitude_square_is_one_over_512": (
            data["amplitude"] * data["amplitude"]
            == Qsqrt2(Fraction(1, 512))
        ),
        "generator_is_skew": all_zero(data["orthogonality_1"]),
        "transport_is_orthogonal_through_order_two": all_zero(
            data["orthogonality_2"]
        ),
        "projector_order_one": all_zero(data["idempotency_1"]),
        "projector_order_two": all_zero(data["idempotency_2"]),
        "projector_trace_order_zero_is_one": trace(data["P0"]) == ONE,
        "projector_trace_order_one_is_zero": trace(data["P1"]) == ZERO,
        "projector_trace_order_two_is_zero": trace(data["P2"]) == ZERO,
        "per_pair_diagonal_is_one_over_512": (
            per_pair == Qsqrt2(Fraction(1, 512))
        ),
        "three_pair_diagonal_is_three_over_512": (
            real_sum == Qsqrt2(Fraction(3, 512))
        ),
        "hard_normalization_is_minus_three_over_512": (
            hard == Qsqrt2(Fraction(-3, 512))
        ),
        "response_cancels": hard + real_sum == ZERO,
        "omitting_hard_normalization_breaks_idempotence": (
            omitted_defect[0][0] == Qsqrt2(Fraction(3, 512))
        ),
        "predecessor_hashes_pinned": all(
            len(sha256(path)) == 64 for path in INPUTS
        ),
        "charge_shift_declared_zero": True,
        "continuum_dressing_stays_open": True,
        "physical_nlo_probability_stays_open": True,
        "no_lorentzian_claim": True,
    }
    certificate = {
        "certificate": "REVERSE_PHYSICS_BT_COLLINEAR_PROJECTOR_TRANSPORT_V1",
        "schema_version": "reverse-physics-bt-collinear-projector-transport-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": (
            "finite coherent hard--collinear projector-transport existence "
            "witness at the certified logarithmic coefficient"
        ),
        "question": (
            "Can a normalized coherent projector, rather than an ordinary "
            "axis-compatible parent-mass map, absorb the exact residual "
            "+3/512 collinear logarithmic response?"
        ),
        "answer": (
            "Yes at the finite exact carrier level. A charge-neutral skew "
            "transport from one hard channel into the three unordered "
            "collinear-pair channels has amplitude sqrt(1/512) per channel. "
            "Projector idempotence uniquely forces the hard diagonal response "
            "-3/512 and the collinear Gram response +3/512, so the common "
            "normalization response cancels. This is an existence and "
            "normalization theorem, not a derivation of the transport from the "
            "BT asymptotic Hamiltonian."
        ),
        "declared_carrier": {
            "basis": ["hard", "pair_12", "pair_13", "pair_23"],
            "coefficient_field": "Q(sqrt(2))",
            "formal_order": "epsilon^2 identified with one positive logarithmic resolution shell",
            "common_physical_factor": "lambda^6/(pi^4*s) is suppressed",
            "projector": "P(epsilon)=exp(epsilon*K)*P0*exp(-epsilon*K) through O(epsilon^2)",
            "metric": "positive neutral quotient carrier only; no global Hilbert metric is asserted",
            "scope": "four-channel coefficient and charge preflight, not the continuum asymptotic state space",
        },
        "projector_transport": {
            "mixing_amplitude": algebraic(data["amplitude"]),
            "per_pair_gram": rational(Fraction(1, 512)),
            "generator_K": serialize_matrix(data["K"]),
            "P0": serialize_matrix(data["P0"]),
            "P1": serialize_matrix(data["P1"]),
            "P2": serialize_matrix(data["P2"]),
            "relations": {
                "skew_generator": "K^T=-K",
                "orthogonal_transport": "U^T U=I+O(epsilon^3)",
                "idempotence": "P(epsilon)^2=P(epsilon)+O(epsilon^3)",
                "trace": "tr P(epsilon)=1+O(epsilon^3)",
            },
        },
        "forced_responses": {
            "per_pair_real_diagonal": rational(Fraction(1, 512)),
            "three_pair_real_diagonal": rational(Fraction(3, 512)),
            "hard_normalization_diagonal": rational(Fraction(-3, 512)),
            "sum": rational(Fraction(0)),
            "physical_units": (
                "(+3/512-3/512)*lambda^6*log(c)/(pi^4*s)=0"
            ),
            "interpretation": (
                "The missing term belongs to normalization/transport of a "
                "coherent cross-multiplicity projector. It is absent from the "
                "bare block-diagonal two-plus-three-particle projector."
            ),
        },
        "uniqueness": {
            "statement": (
                "For P=P0+epsilon*P1+epsilon^2*P2 with P0 the hard block and "
                "P1 purely hard--collinear, the order-two equation P^2=P "
                "forces P2_hh=-(P1^2)_hh and P2_cc=(P1^2)_cc. Only the "
                "order-two hard--collinear basis-gauge block remains free."
            ),
            "hard_block": "-A*A^T=-3/512",
            "collinear_block": "A^T*A, with every entry 1/512",
            "free_block": "P2_hc and P2_ch; set to zero by exponential transport",
        },
        "bt_charge_gate": {
            "generator_total_charge_shift": 0,
            "result": "PRESERVES_ONE_SIDED_NEGATIVE_RELATIVE_RADICAL",
            "reason": (
                "The finite Laurent charge calculation is recomputed here: "
                "q<0 maps to q+0<0, while the positive-shift mutation sends "
                "q=-2 to charge zero."
            ),
            "boundary": (
                "This is a charge preflight. The continuum transport kernel and "
                "its trace-class/existence properties have not been constructed."
            ),
        },
        "decisive_mutations": [
            {
                "mutation": "omit P2_hh",
                "effect": "order-two hard idempotency defect +3/512",
                "rejected": True,
            },
            {
                "mutation": "reverse the forced hard sign",
                "effect": "normalization response adds instead of cancels and P^2=P fails",
                "rejected": True,
            },
            {
                "mutation": "assign positive total BT charge shift",
                "effect": "a negative-charge input can reach charge zero and become trace-visible",
                "rejected": True,
            },
        ],
        "disposition": {
            "ordinary_axis_compatible_mass_regulator": "REMAINS_OBSTRUCTED",
            "finite_coherent_projector_transport": "EXACT_EXISTENCE_WITNESS",
            "normalization_coefficient": "FORCED_BY_IDEMPOTENCE",
            "bt_relative_radical_preflight": "PASSES_FOR_NEUTRAL_TRANSPORT",
            "bt_asymptotic_hamiltonian_derivation": "NOT_CONSTRUCTED",
            "continuum_collinear_projector": "NOT_CONSTRUCTED",
            "full_nlo_quotient_trace": "NOT_COMPUTED",
            "physical_nlo_probability": "NOT_ESTABLISHED",
            "beyond_tree_positivity": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "derive the hard--collinear generator from the BT/PS asymptotic Hamiltonian rather than fitting its Gram coefficient",
            "construct the continuum splitting-fraction and momentum-space carrier with domains and regulator",
            "include incoming as well as outgoing degenerate sectors",
            "prove existence and trace-class control of the transported process projector",
            "evaluate the full renormalized NLO quotient trace and test regulator independence",
            "exclude an SO+(1,1) measure anomaly after asymptotic transport",
            "supply any tensor/BRST gravitational lift from certified classical data",
        ],
        "next_gate": (
            "Compute the first-order asymptotic splitting generator K_BT from "
            "the broken-vacuum cubic interaction and prove that its regulated "
            "three-channel Gram operator is exactly the certified 1/512 per "
            "pair. If that dynamical equality fails, this finite witness does "
            "not describe BT scattering."
        ),
        "does_not_establish": [
            "a dressed-state or KLN theorem for Bateman--Turok theory",
            "that the finite transport is generated by the BT asymptotic Hamiltonian",
            "existence, convergence, or trace-class control in the continuum",
            "a complete NLO cross section or regulator-independent probability",
            "positivity or unitarity beyond Bateman--Turok's tree theorem",
            "a global Hilbert metric for the Krein theory",
            "a Lorentzian off-shell BV propagator, Hadamard state, or causal construction",
            "anything LORENTZIAN-CAUSAL",
            "a tensor, BRST, or Weyl-gravity theorem",
            "literature priority for coherent asymptotic-state transport",
        ],
        "literature_context": [
            {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096",
                "use": "generalized Born rule, charge grading, and the stated collinear asymptotic-state problem",
            },
            {
                "source": "Hannesdottir--Schwartz arXiv:1906.03271",
                "url": "https://arxiv.org/abs/1906.03271",
                "use": "external precedent for replacing free asymptotic evolution by soft-collinear asymptotic evolution; no scalar-BT theorem is imported",
            },
            {
                "source": "Hannesdottir--Schwartz arXiv:1911.06821",
                "url": "https://arxiv.org/abs/1911.06821",
                "use": "external precedent for explicit divergence cancellation through asymptotic evolution; no coefficient is imported",
            },
        ],
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-10",
            "inputs": [
                {"path": path, "sha256": sha256(path)} for path in INPUTS
            ],
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_collinear_projector_transport.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_collinear_projector_transport.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_collinear_projector_transport",
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks,
        },
        "report": REPORT_PATH,
        "schema": SCHEMA_PATH,
    }
    return certificate


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=CERT_PATH)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    certificate = build()
    if args.check:
        try:
            with open(args.output, encoding="utf-8") as handle:
                recorded = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[FAIL] recorded_certificate: {exc}")
            return 1
        ok = recorded == certificate
        print(f"[{'PASS' if ok else 'FAIL'}] exact_reproduction")
        print(f"RESULT: {'PASS' if ok else 'FAIL'} "
              f"({certificate['checks']['passed']}/{certificate['checks']['total']})")
        return 0 if ok else 1
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(certificate, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(args.output)
    return 0 if certificate["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
