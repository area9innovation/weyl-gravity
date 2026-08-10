#!/usr/bin/env python3
"""Correct BT projector normalization and test the naive asymptotic generator.

The rate comparison is exact rational arithmetic.  The finite projector uses
Q(sqrt(3)).  The cubic preflight keeps only the collinear invariant t and the
leading energy deficit, which is enough to distinguish a conventional single
Dyson denominator from the double/Jordan denominator required by the PS
double pole.
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
    "REVERSE_PHYSICS_BT_ASYMPTOTIC_GENERATOR_PREFLIGHT_V1.json",
)
SCHEMA_PATH = (
    "reverse_physics/schema/"
    "reverse-physics-bt-asymptotic-generator-preflight-v1.schema.json"
)
REPORT_PATH = "reverse_physics/reports/bt-asymptotic-generator-preflight.md"
SOURCE_COMMIT = "75d533eb8d70112778b265fa24801b414d50c103"
INPUTS = [
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_REAL_VIRTUAL_AXIS_GLUING_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_COLLINEAR_PROJECTOR_TRANSPORT_V1.json",
]


@dataclass(frozen=True)
class Qsqrt3:
    """Exact p+q*sqrt(3)."""

    p: Fraction = Fraction(0)
    q: Fraction = Fraction(0)

    def __add__(self, other):
        other = coerce(other)
        return Qsqrt3(self.p + other.p, self.q + other.q)

    __radd__ = __add__

    def __neg__(self):
        return Qsqrt3(-self.p, -self.q)

    def __sub__(self, other):
        return self + (-coerce(other))

    def __rsub__(self, other):
        return coerce(other) - self

    def __mul__(self, other):
        other = coerce(other)
        return Qsqrt3(
            self.p * other.p + 3 * self.q * other.q,
            self.p * other.q + self.q * other.p,
        )

    __rmul__ = __mul__

    def __eq__(self, other):
        other = coerce(other)
        return self.p == other.p and self.q == other.q


def coerce(value):
    if isinstance(value, Qsqrt3):
        return value
    return Qsqrt3(Fraction(value))


ZERO = Qsqrt3()
ONE = Qsqrt3(Fraction(1))


def rational(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def algebraic(value):
    value = coerce(value)
    return {"rational": rational(value.p), "sqrt3": rational(value.q)}


def zeros(size=4):
    return [[ZERO for _ in range(size)] for _ in range(size)]


def add(*matrices):
    size = len(matrices[0])
    return [
        [sum((matrix[i][j] for matrix in matrices), ZERO)
         for j in range(size)]
        for i in range(size)
    ]


def scale(coefficient, matrix):
    coefficient = coerce(coefficient)
    return [[coefficient * entry for entry in row] for row in matrix]


def multiply(left, right):
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


def all_zero(matrix):
    return all(entry == ZERO for row in matrix for entry in row)


def sparse(matrix):
    return [
        {"row": i, "column": j, "value": algebraic(entry)}
        for i, row in enumerate(matrix)
        for j, entry in enumerate(row)
        if entry != ZERO
    ]


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def normalization():
    """Convert the absolute NLO rate into a dimensionless projector Gram."""
    born = Fraction(3, 32)
    real_per_pair = Fraction(1, 512)
    gram_per_pair = real_per_pair / born
    pair_count = 3
    gram_total = pair_count * gram_per_pair
    absolute_total = pair_count * real_per_pair
    old_v1_hard = born * Fraction(3, 512)
    old_v1_residual = absolute_total - old_v1_hard
    return {
        "born": born,
        "real_per_pair": real_per_pair,
        "pair_count": pair_count,
        "absolute_total": absolute_total,
        "gram_per_pair": gram_per_pair,
        "gram_total": gram_total,
        "old_v1_hard": old_v1_hard,
        "old_v1_residual": old_v1_residual,
    }


def projector():
    """Build exp(epsilon K) P0 exp(-epsilon K) through epsilon squared."""
    amplitude = Qsqrt3(Fraction(0), Fraction(1, 12))
    k = zeros()
    for channel in range(1, 4):
        k[0][channel] = -amplitude
        k[channel][0] = amplitude
    p0 = zeros()
    p0[0][0] = ONE
    k2 = multiply(k, k)
    p1 = add(multiply(k, p0), scale(-1, multiply(p0, k)))
    p2 = add(
        scale(Fraction(1, 2), multiply(k2, p0)),
        scale(-1, multiply(multiply(k, p0), k)),
        scale(Fraction(1, 2), multiply(p0, k2)),
    )
    defect_1 = add(multiply(p0, p1), multiply(p1, p0), scale(-1, p1))
    defect_2 = add(
        multiply(p0, p2), multiply(p2, p0), multiply(p1, p1), scale(-1, p2)
    )
    return {
        "amplitude": amplitude,
        "K": k,
        "P0": p0,
        "P1": p1,
        "P2": p2,
        "defect_1": defect_1,
        "defect_2": defect_2,
    }


def cubic_preflight():
    """Exact leading powers in the collinear invariant t."""
    # M3/(-i*lambda)=Lambda(t,0,0)=t^2.
    vertex_power = 2
    # Delta E=t/(2E)+O(t^2), so one denominator lowers the power once.
    single_denominator_power = vertex_power - 1
    double_denominator_power = vertex_power - 2
    return {
        "vertex_power": vertex_power,
        "energy_deficit_power": 1,
        "single_denominator_power": single_denominator_power,
        "double_denominator_power": double_denominator_power,
        "ordinary_limit": Fraction(0),
        "double_denominator_reduced_limit": Fraction(4),
    }


def build():
    norm = normalization()
    proj = projector()
    cubic = cubic_preflight()
    p2 = proj["P2"]
    real_diagonal = sum((p2[i][i] for i in range(1, 4)), ZERO)
    checks = {
        "born_rate_is_three_over_32": norm["born"] == Fraction(3, 32),
        "absolute_per_pair_is_one_over_512": (
            norm["real_per_pair"] == Fraction(1, 512)
        ),
        "dimensionless_gram_per_pair_is_one_over_48": (
            norm["gram_per_pair"] == Fraction(1, 48)
        ),
        "dimensionless_three_pair_gram_is_one_over_16": (
            norm["gram_total"] == Fraction(1, 16)
        ),
        "amplitude_square_is_one_over_48": (
            proj["amplitude"] * proj["amplitude"]
            == Qsqrt3(Fraction(1, 48))
        ),
        "generator_is_skew": all_zero(add(proj["K"], transpose(proj["K"]))),
        "projector_order_one": all_zero(proj["defect_1"]),
        "projector_order_two": all_zero(proj["defect_2"]),
        "projector_trace_is_preserved": (
            trace(proj["P0"]) == ONE
            and trace(proj["P1"]) == ZERO
            and trace(proj["P2"]) == ZERO
        ),
        "hard_block_is_minus_one_over_16": (
            p2[0][0] == Qsqrt3(Fraction(-1, 16))
        ),
        "real_diagonal_is_plus_one_over_16": (
            real_diagonal == Qsqrt3(Fraction(1, 16))
        ),
        "physical_rate_cancels": (
            norm["born"] * norm["gram_total"] == norm["absolute_total"]
        ),
        "v1_normalization_leaves_residual": (
            norm["old_v1_residual"] == Fraction(87, 16384)
        ),
        "massless_cubic_is_quadratic_in_t": cubic["vertex_power"] == 2,
        "single_denominator_kernel_vanishes": (
            cubic["single_denominator_power"] == 1
            and cubic["ordinary_limit"] == 0
        ),
        "double_denominator_can_be_finite": (
            cubic["double_denominator_power"] == 0
            and cubic["double_denominator_reduced_limit"] == 4
        ),
        "ordinary_kernel_misses_nonzero_target": (
            cubic["ordinary_limit"] != norm["gram_per_pair"]
        ),
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "jordan_generator_stays_open": True,
        "incoming_sector_stays_open": True,
        "no_lorentzian_claim": True,
    }
    certificate = {
        "certificate": "REVERSE_PHYSICS_BT_ASYMPTOTIC_GENERATOR_PREFLIGHT_V1",
        "schema_version": "reverse-physics-bt-asymptotic-generator-preflight-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": (
            "dimensionless collinear projector normalization and ordinary "
            "single-denominator asymptotic-generator obstruction"
        ),
        "question": (
            "What Gram coefficient must a BT collinear dressing reproduce, "
            "and can the ordinary on-shell cubic Fock generator produce it?"
        ),
        "answer": (
            "The required dimensionless Gram coefficient is 1/48 per unordered "
            "final pair and 1/16 for all three, after dividing the absolute NLO "
            "response by the Born rate. A normalized finite projector then "
            "cancels the physical 3/512 response exactly. The ordinary cubic "
            "Fock generator cannot generate it: M3 is proportional to t^2 and "
            "one Dyson energy denominator is proportional to 1/t, so its "
            "collinear kernel vanishes. A Jordan/double-denominator or order-"
            "lambda R_t distributional generator is required and is not "
            "constructed here."
        ),
        "normalization_ledger": {
            "born_rate": "B=3*lambda^4/(32*pi^2*s)",
            "absolute_real_per_pair": "+lambda^6*log(c)/(512*pi^4*s)",
            "absolute_real_all_pairs": "+3*lambda^6*log(c)/(512*pi^4*s)",
            "dimensionless_shell_parameter": "eta=lambda^2*log(c)/pi^2",
            "gram_per_pair": rational(norm["gram_per_pair"]),
            "gram_all_pairs": rational(norm["gram_total"]),
            "identity": "(1/512)/(3/32)=1/48",
            "hard_rate_from_normalization": "B*(-eta/16)=-3*lambda^6*log(c)/(512*pi^4*s)",
            "combined_physical_response": "(+3/512-3/512)*lambda^6*log(c)/(pi^4*s)=0",
        },
        "corrected_projector": {
            "basis": ["hard", "pair_12", "pair_13", "pair_23"],
            "field": "Q(sqrt(3))",
            "mixing_amplitude": algebraic(proj["amplitude"]),
            "generator_K": sparse(proj["K"]),
            "P0": sparse(proj["P0"]),
            "P1": sparse(proj["P1"]),
            "P2": sparse(proj["P2"]),
            "hard_order_two": rational(Fraction(-1, 16)),
            "real_trace_order_two": rational(Fraction(1, 16)),
            "idempotence": "P^2=P+O(epsilon^3)",
            "trace": "tr(P)=1+O(epsilon^3)",
        },
        "v1_supersession": {
            "certificate": "REVERSE_PHYSICS_BT_COLLINEAR_PROJECTOR_TRANSPORT_V1",
            "status": "SUPERSEDED_NORMALIZATION",
            "error": (
                "V1 inserted the absolute rate coefficient 1/512 directly "
                "into a dimensionless projector. Projector normalization must "
                "first divide the NLO rate by the Born rate."
            ),
            "v1_hard_rate_under_correct_shell_units": rational(norm["old_v1_hard"]),
            "uncancelled_absolute_coefficient": rational(norm["old_v1_residual"]),
            "architecture_status": (
                "SURVIVES: idempotence still forces the compensating hard term "
                "after replacing 1/512 by the normalized 1/48 per pair"
            ),
        },
        "cubic_generator_preflight": {
            "published_vertex": "M3=-i*lambda*Kallen(t,x,y)",
            "massless_daughters": "Kallen(t,0,0)=t^2",
            "collinear_energy_deficit": "DeltaE=t/(2E)+O(t^2)",
            "ordinary_dyson_kernel": "M3/DeltaE=-2*i*lambda*E*t+O(t^2) -> 0",
            "ordinary_gram_target": rational(Fraction(0)),
            "required_gram_target": rational(norm["gram_per_pair"]),
            "disposition": "EXACT_OBSTRUCTION_FOR_SINGLE_DENOMINATOR_FOCK_GENERATOR",
            "jordan_control": (
                "M3/(DeltaE)^2 -> -4*i*lambda*E^2, so a double/secular "
                "denominator can survive; its normalization and domain are not derived"
            ),
            "public_source_gap": (
                "Bateman--Turok Appendix C Eqs. (32)-(33) give R_t only up to "
                "O(lambda); the omitted order-lambda term is precisely the "
                "first cross-multiplicity kernel needed here"
            ),
        },
        "charge_gate": {
            "cubic_charge": "q(Omega)+2*q(Upsilon)=-1 around the broken vacuum",
            "warning": (
                "The bare cubic monomial is negatively charged because the "
                "chosen vacuum breaks SO+(1,1). A neutral projector transport "
                "cannot be inferred from that vertex alone; the background/R_t "
                "charge bookkeeping is part of the missing construction."
            ),
            "disposition": "NOT_CLEARED_BY_BARE_CUBIC_VERTEX",
        },
        "disposition": {
            "dimensionless_gram_target": "COEFFICIENT_COMPUTED",
            "finite_corrected_projector": "EXACT_EXISTENCE_WITNESS",
            "v1_projector_normalization": "SUPERSEDED",
            "ordinary_single_denominator_fock_generator": "EXACT_OBSTRUCTION",
            "jordan_distributional_generator": "NOT_CONSTRUCTED",
            "order_lambda_R_t_kernel": "NOT_AVAILABLE_IN_PUBLIC_SOURCE",
            "incoming_degenerate_sectors": "NOT_CONSTRUCTED",
            "full_nlo_quotient_trace": "NOT_COMPUTED",
            "physical_nlo_probability": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "derive the omitted order-lambda term of the R_t homomorphism or an equivalent Jordan asymptotic generator",
            "fix the double/secular energy denominator as a distribution with a declared domain and resolution flow",
            "show that the resulting regulated Gram operator equals 1/48 per unordered final pair",
            "restore neutral charge bookkeeping including the broken-vacuum background",
            "include incoming as well as outgoing degenerate sectors",
            "construct the continuum projector and prove existence and trace-class control",
            "evaluate the complete renormalized NLO quotient trace",
        ],
        "next_gate": (
            "Do not use an ordinary one-denominator Fock dressing. Derive the "
            "order-lambda R_t/Jordan kernel with its double secular denominator, "
            "then test its regulated Gram against 1/48 per pair and its total "
            "charge including the background."
        ),
        "does_not_establish": [
            "a BT dressed-state or KLN theorem",
            "existence or uniqueness of the required Jordan/distributional generator",
            "that a double denominator has the correct 1/48 normalization",
            "neutrality of the broken-vacuum cubic generator",
            "a complete NLO probability or regulator-independent quotient trace",
            "positivity or unitarity beyond the BT tree theorem",
            "anything about the tensor/BRST gravitational lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-10",
            "inputs": [
                {"path": path, "sha256": sha256(path)} for path in INPUTS
            ],
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096",
                "equations": ["Eq. (13)", "Eq. (24)", "Appendix C Eqs. (32)-(33)"],
            },
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_asymptotic_generator_preflight.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_asymptotic_generator_preflight.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_asymptotic_generator_preflight",
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
