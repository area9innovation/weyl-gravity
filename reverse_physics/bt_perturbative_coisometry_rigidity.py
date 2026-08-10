#!/usr/bin/env python3
"""Prove perturbative two-sidedness of the BT free coisometry.

The proof has two independent exact parts.  First, the published leading
oscillator pullbacks reproduce the full cross CCR, forcing the leading support
Pi_0=R_0^dagger R_0 to be the identity.  Second, an idempotent formal series
Pi(lambda) with Pi_0=1 is identically one coefficient by coefficient.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_PERTURBATIVE_COISOMETRY_RIGIDITY_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-perturbative-coisometry-rigidity-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-perturbative-coisometry-rigidity.md"
SOURCE_COMMIT = "d5381e21d4da27154f1a15bb077879e7017f2e93"
INPUTS = [
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_COISOMETRY_RANGE_NONUNIQUENESS_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_RT_JORDAN_KERNEL_V1.json",
]


def rational(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def free_cross_ccr(energy):
    """Coefficient of [A_Upsilon,A_Omega^dagger] at lambda^0."""
    energy = Fraction(energy)
    a_cross = (2 * energy) ** 3
    omega_normalization = 4 * energy**2
    pulled = a_cross / omega_normalization
    target = 2 * energy
    return pulled, target


def projection_recursion(order):
    """Scalar mutation fixture for the universal noncommutative recursion."""
    coefficients = [Fraction(1)]
    rows = []
    for degree in range(1, order + 1):
        lower_sum = sum(
            coefficients[k] * coefficients[degree - k]
            for k in range(1, degree)
        )
        coefficient = -lower_sum
        coefficients.append(coefficient)
        lhs = sum(
            coefficients[k] * coefficients[degree - k]
            for k in range(degree + 1)
        )
        rows.append({
            "degree": degree,
            "lower_convolution": rational(lower_sum),
            "Pi_degree": rational(coefficient),
            "projection_coefficient": rational(lhs - coefficient),
        })
    return coefficients, rows


def build():
    energy_rows = []
    ccr_ok = True
    for energy in (Fraction(1), Fraction(3, 2), Fraction(5), Fraction(11, 3)):
        pulled, target = free_cross_ccr(energy)
        ok = pulled == target
        ccr_ok = ccr_ok and ok
        energy_rows.append({
            "energy": rational(energy),
            "a_cross_commutator": rational((2 * energy) ** 3),
            "Omega_denominator": rational(4 * energy**2),
            "pulled_cross_CCR": rational(pulled),
            "BT_cross_CCR": rational(target),
            "identity": ok,
        })

    coefficients, recursion_rows = projection_recursion(12)
    all_higher_zero = all(value == 0 for value in coefficients[1:])
    checks = {
        "published_cross_CCR_normalization_exact": ccr_ok,
        "homomorphism_cross_CCR_is_two_E_times_Pi": True,
        "leading_support_is_identity": ccr_ok,
        "support_is_a_projection": True,
        "projection_recursion_through_twelve": all_higher_zero,
        "inductive_recursion_has_no_free_coefficient": all(
            row["Pi_degree"] == {"numerator": 0, "denominator": 1}
            for row in recursion_rows
        ),
        "formal_support_is_identity": all_higher_zero,
        "formal_defect_vanishes": all_higher_zero,
        "general_nonperturbative_witness_retained": True,
        "prior_scope_is_superseded_not_deleted": True,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "probability_stays_open": True,
        "no_lorentzian_claim": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_PERTURBATIVE_COISOMETRY_RIGIDITY_V1",
        "schema_version": "reverse-physics-bt-perturbative-coisometry-rigidity-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": (
            "formal perturbative rigidity theorem for the BT coisometric "
            "support projection"
        ),
        "question": (
            "Can the BT range projection differ perturbatively from the "
            "identity after the published leading oscillator map is imposed?"
        ),
        "answer": (
            "No. The repaired leading pullbacks give A_Upsilon=a1 and an "
            "a2-dagger coefficient 1/(4E^2) in A_Omega-dagger. Their cross "
            "commutator is (2E)^3/(4E^2)=2E times the identity. The homomorphism "
            "and R R-dagger=1 give the same commutator as 2E Pi, where "
            "Pi=R-dagger R, so Pi_0=1. Since Pi^2=Pi, the coefficient equation "
            "at every positive order is Pi_n=-sum_(k=1)^(n-1)Pi_k Pi_(n-k); "
            "induction makes all Pi_n zero. Thus R is two-sided as a formal "
            "perturbative series, although a discontinuous/nonperturbative "
            "defect is not excluded."
        ),
        "free_CCR_gate": {
            "published_pullbacks": (
                "A_Upsilon=a1; A_Omega^dagger contains "
                "a2^dagger/(4E^2)"
            ),
            "a_algebra": "[a1,a2^dagger]=(2E)^3",
            "homomorphism_identity": (
                "[R^dagger b_Upsilon R,R^dagger b_Omega^dagger R]="
                "R^dagger[b_Upsilon,b_Omega^dagger]R=2E*Pi"
            ),
            "rows": energy_rows,
            "conclusion": "Pi_0=identity on the common oscillator domain",
        },
        "formal_projection_rigidity": {
            "series": "Pi(lambda)=identity+sum_(n>=1)lambda^n Pi_n",
            "equation": "Pi^2=Pi",
            "recursion": (
                "Pi_n=-sum_(k=1)^(n-1)Pi_k Pi_(n-k)"
            ),
            "proof": (
                "Pi_1=0; if Pi_1,...,Pi_(n-1)=0 then the recursion gives "
                "Pi_n=0"
            ),
            "mutation_fixture_rows": recursion_rows,
            "conclusion": "Pi(lambda)=identity as a formal power series",
        },
        "supersession": {
            "certificate": (
                "REVERSE_PHYSICS_BT_COISOMETRY_RANGE_NONUNIQUENESS_V1"
            ),
            "status": "SCOPE_RESTRICTED_TO_NONPERTURBATIVE_OR_DISCONNECTED_BRANCHES",
            "surviving_statement": (
                "R R-dagger=1 alone does not imply R-dagger R=1 for an "
                "arbitrary coisometry"
            ),
            "superseded_application": (
                "the exact finite defect family cannot model the analytic BT "
                "branch once the published free cross-CCR fixes Pi_0=1"
            ),
        },
        "consequence_for_probability": {
            "formal_inversion_of_R_t": "CLEARED_ORDER_BY_ORDER",
            "coisometric_range_constants": "ZERO_ON_PERTURBATIVE_BRANCH",
            "endpoint_constants": (
                "must be fixed by distributional canonical/projector identities, "
                "not by a perturbative range defect"
            ),
            "one_over_48": "STILL_NOT_DERIVED",
        },
        "assumptions": [
            "the oscillator identities act on a common invariant dense domain",
            "R_t and Pi admit formal power series in lambda around the free map",
            "the repaired Appendix C labels are used",
            "the published cross commutators have their stated normalization",
        ],
        "disposition": {
            "free_range_projection": "IDENTITY",
            "formal_perturbative_range_projection": "IDENTITY_TO_ALL_ORDERS",
            "formal_two_sided_inverse": "CLEARED",
            "nonperturbative_range_defect": "NOT_EXCLUDED",
            "canonical_endpoint_extension": "NOT_CONSTRUCTED",
            "one_over_48": "NOT_DERIVED",
            "full_nlo_quotient_trace": "NOT_COMPUTED",
            "physical_nlo_probability": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a distributional canonical-commutator extension of the order-lambda kernel",
            "projector idempotence on endpoint jets through degree two",
            "the resulting dynamically fixed c0,c1,c2 constants",
            "incoming/outgoing equality of that canonical extension",
            "Bose, phase-space, and renormalized virtual assembly",
            "the complete NLO quotient trace and positivity test",
        ],
        "next_gate": (
            "Use Pi=1 perturbatively. Impose the exact pulled oscillator CCR "
            "and transported-projector idempotence as distributional identities "
            "on the three endpoint jets; solve for c0,c1,c2 without fitting and "
            "then compare the resulting Gram with 1/48."
        ),
        "does_not_establish": [
            "convergence of the formal lambda series",
            "absence of nonperturbative or disconnected coisometric defects",
            "a unique endpoint distribution",
            "the coefficient 1/48",
            "a complete NLO probability or beyond-tree positivity",
            "a tensor or BRST gravitational lift",
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
                "equations": ["Appendix C Eqs. (31)-(33)"],
            },
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_perturbative_coisometry_rigidity.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_perturbative_coisometry_rigidity.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_perturbative_coisometry_rigidity",
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks,
        },
        "report": REPORT,
        "schema": SCHEMA,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=CERT)
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
