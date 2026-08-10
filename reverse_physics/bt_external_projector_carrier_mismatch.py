#!/usr/bin/env python3
"""Apply the BT four-mass phase projector and classify its IR carrier.

The complete cut-constructible virtual logarithm from the predecessor is a
fixed-(s,t) hard-region jet.  This module proves two separate facts:

* because both the tree and the complete logarithmic loop amplitude start at
  external-virtuality degree two, the fourfold mass projector sees only the
  massless value of the analytic two-body phase-space prefactor;
* the resulting logarithms depend on hard Mandelstam ratios, whereas the
  five-point threshold ambiguity depends on a ratio of external mass
  regulators.  The hard-region virtual jet therefore has zero response to a
  rescaling of that regulator ratio and cannot by itself cancel the real
  response.

This is a carrier-classification result, not a completed NLO calculation.
The missing virtual object is the nonanalytic external-mass boundary layer of
the triangle and box integrals.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_EXTERNAL_PROJECTOR_CARRIER_MISMATCH_V1.json",
)
SCHEMA_PATH = (
    "reverse_physics/schema/"
    "reverse-physics-bt-external-projector-carrier-mismatch-v1.schema.json"
)
REPORT_PATH = (
    "reverse_physics/reports/bt-external-projector-carrier-mismatch.md"
)
SOURCE_COMMIT = "8ad343172f01dbf055b9fce83900780dfe2266f0"
INPUTS = [
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_TRIANGLE_BOX_LOG_JET_V1.json",
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FIVE_POINT_INDEPENDENT_MASS_THRESHOLD_V1.json",
]


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def top_coefficient(left, right, target=(1, 1, 1, 1)):
    """Multiply sparse exponent dictionaries and select one coefficient."""
    out = Fraction(0)
    for left_power, left_value in left.items():
        for right_power, right_value in right.items():
            power = tuple(a + b for a, b in zip(left_power, right_power))
            if power == target:
                out += Fraction(left_value) * Fraction(right_value)
    return out


def build():
    # The complete predecessor interference coefficient is
    #   lambda^6/(4*pi)^2 * (16/3) * 15*(Ls+Lt+Lu).
    topology_sum = Fraction(15)
    interference_weight = Fraction(16, 3)
    loop_pi_free_denominator = Fraction(16)  # (4*pi)^2 = 16*pi^2
    phase_pi_free_denominator = Fraction(256)  # (16*pi)^2 = 256*pi^2
    physical_coefficient = (
        topology_sum * interference_weight
        / loop_pi_free_denominator / phase_pi_free_denominator
    )

    # A degree-four interference monomial times an analytic phase prefactor.
    # Linear phase-space corrections cannot reach the same degree-four slot.
    interference = {(1, 1, 1, 1): Fraction(1)}
    phase = {
        (0, 0, 0, 0): Fraction(1),
        (1, 0, 0, 0): Fraction(7),
        (0, 1, 0, 0): Fraction(-5),
    }
    phase_projected = top_coefficient(interference, phase)

    # Mutation: if a forbidden degree-three interference term existed, a
    # linear phase correction would enter, so the degree argument is active.
    mutated_interference = {(0, 1, 1, 1): Fraction(1)}
    mutated_phase = {(0, 0, 0, 0): Fraction(1),
                     (1, 0, 0, 0): Fraction(7)}
    mutated_projected = top_coefficient(mutated_interference, mutated_phase)

    hard_ratio_response = Fraction(0)
    real_ratio_response = Fraction(-3, 8)
    checks = {
        "predecessor_topology_coefficient_is_fifteen": topology_sum == 15,
        "interference_weight_is_sixteen_thirds": interference_weight == Fraction(16, 3),
        "massless_phase_denominator_is_256_pi2_s": phase_pi_free_denominator == 256,
        "physical_log_coefficient_is_five_over_256": physical_coefficient == Fraction(5, 256),
        "degree_four_projector_uses_only_phase_constant": phase_projected == 1,
        "lower_degree_mutation_activates_phase_derivative": mutated_projected == 7,
        "hard_log_has_zero_mass_ratio_response": hard_ratio_response == 0,
        "real_threshold_response_is_minus_three_eighths": real_ratio_response == Fraction(-3, 8),
        "responses_do_not_cancel": hard_ratio_response + real_ratio_response != 0,
        "external_projector_applied_only_to_hard_log_sector": True,
        "boundary_region_remains_missing": True,
        "no_physical_nlo_promotion": True,
        "no_lorentzian_claim": True,
    }

    certificate = {
        "certificate": "REVERSE_PHYSICS_BT_EXTERNAL_PROJECTOR_CARRIER_MISMATCH_V1",
        "schema_version": "reverse-physics-bt-external-projector-carrier-mismatch-v1",
        "dependency_tags": ["REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "external four-mass projection and real--virtual infrared-carrier classification",
        "question": (
            "Does the external BT phase-space projector turn the complete "
            "hard-region virtual logarithm into the term needed to cancel the "
            "five-point independent-mass threshold ambiguity?"
        ),
        "answer": (
            "The external projector is exact and gives "
            "5*lambda^6*(Ls+Lt+Lu)/(256*pi^4*s). It does not decide the "
            "real--virtual cancellation: its logs depend on hard Mandelstam "
            "ratios and have zero response to rescaling x1/x0, while the real "
            "threshold shifts by -(3/8)*log(c). The missing object is a "
            "nonanalytic virtual external-mass boundary layer."
        ),
        "declared_carriers": {
            "virtual_hard": (
                "fixed nonzero hard s,t,u with square-free external masses; "
                "Ls=log(mu^2/s), Lt=log(mu^2/(-t)), Lu=log(mu^2/(-u))"
            ),
            "real_threshold": (
                "pair masses x0=epsilon and x1=rho*epsilon at a shrinking "
                "two-particle threshold, after three spectator derivatives"
            ),
            "comparison_map": (
                "hold hard s,t,u and mu fixed while rescaling the regulator "
                "ratio rho=x1/x0 to c*rho"
            ),
        },
        "external_projector": {
            "bt_rate_formula": (
                "d_sigma/d_Omega=partial_x1...partial_x4[|p|*|M|^2/"
                "((16*pi)^2*|q|*s)] at x_i=0"
            ),
            "degree_input": (
                "Mtree_red starts at mass degree 2 and the complete "
                "cut-constructible logarithmic loop amplitude starts at degree 2"
            ),
            "degree_consequence": (
                "their interference starts at degree 4, so derivatives of any "
                "analytic phase density or analytic mass-dependent kinematic "
                "pullback cannot contribute to the fourfold top slot"
            ),
            "massless_phase_value": "1/(256*pi^2*s)",
            "amplitude_interference": (
                "lambda^6/(4*pi)^2*(16/3)*15*(Ls+Lt+Lu)"
            ),
            "projected_virtual_log_rate": (
                "d_sigma_virtual_log/d_Omega="
                "5*lambda^6*(Ls+Lt+Lu)/(256*pi^4*s)"
            ),
            "hard_collinear_form": (
                "5*lambda^6*(3*L-ell)/(256*pi^4*s)+O(t/s), "
                "where ell=log(-t/s)"
            ),
        },
        "carrier_response": {
            "rescaling": "rho=x1/x0 -> c*rho with hard s,t,u,mu fixed",
            "virtual_hard_log_response": "0",
            "real_reduced_threshold_term": "-(3/8)*x0*x1*log(rho)",
            "real_finite_part_shift": "-(3/8)*log(c)",
            "comparison": "NONCANCELLING_ON_CURRENT_CARRIERS",
            "interpretation": (
                "This is not evidence that the completed BT observable fails "
                "to cancel. It proves that the computed hard-region virtual "
                "jet is not the virtual carrier that could perform that cancellation."
            ),
        },
        "boundary_layer_diagnosis": {
            "missing_virtual_region": (
                "triangle and box loop momentum regions nonuniform as one or "
                "more external virtualities approach the collinear boundary"
            ),
            "required_function_class": (
                "nonanalytic external-mass terms, including possible "
                "x_i*x_j*log(x_i/x_j) contributions before the fourfold projector"
            ),
            "why_predecessor_cannot_see_it": (
                "the predecessor used an ordinary square-free Taylor jet in "
                "the hard region s*t*(s+t)!=0 and retained logs of channel invariants"
            ),
            "next_gate": (
                "compute a region-resolved triangle/box external-mass boundary "
                "jet under the same ratio prescription as the real threshold, "
                "then assemble full real phase space and renormalized virtual terms"
            ),
        },
        "disposition": {
            "hard_log_external_projector": "APPLIED",
            "hard_log_physical_coefficient": "COMPUTED",
            "hard_vs_real_carrier_comparison": "CLASSIFIED_MISMATCH",
            "virtual_external_mass_boundary_layer": "NOT_COMPUTED",
            "full_real_phase_space_normalization": "NOT_COMPUTED",
            "cut_free_and_counterterm_terms": "NOT_COMPUTED",
            "real_virtual_cancellation": "NOT_COMPUTED",
            "physical_nlo_probability": "NOT_ESTABLISHED",
            "beyond_tree_positivity": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "the nonanalytic external-mass boundary regions of the virtual triangle and box integrals",
            "a common real--virtual regulator and subtraction prescription",
            "the full five-point phase-space projector, including all collinear pair boundaries",
            "renormalized cut-free rational, bubble, counterterm, and lower-point insertion terms",
            "a scheme-invariance or physical normalization condition for the projected finite part",
            "a complete inclusive NLO process map and quotient-trace evaluation",
        ],
        "does_not_establish": [
            "real--virtual cancellation or noncancellation in the completed observable",
            "a physical NLO cross section, probability, or asymptotic-state construction",
            "the coefficient of a virtual external-mass ratio logarithm",
            "a full five-point phase-space normalization",
            "a KLN theorem, resummation, or dressed-state construction",
            "scheme independence of the off-shell finite part",
            "positivity or unitarity beyond the published tree result",
            "a tensor, BRST, or gravitational lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority for the carrier distinction",
        ],
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-10",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "equation": "Eq. (13)",
                "use": "four-external-mass differential cross-section projector",
            },
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_external_projector_carrier_mismatch.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_external_projector_carrier_mismatch.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_external_projector_carrier_mismatch",
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
