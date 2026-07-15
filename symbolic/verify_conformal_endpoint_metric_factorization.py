#!/usr/bin/env python3
"""Verify the exact endpoint same-bundle scalar-factorization screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.endpoint_metric_factorization import (
    EndpointMetricFactorizationNoGo,
    load_system,
)


CERTIFICATES = ROOT / "covariant_completion" / "certificates"
GENERATED = ROOT / "covariant_completion" / "generated"
INPUT = CERTIFICATES / "curved_prolonged_metric_endpoint_backward_witness_coefficients.json"
OUTPUT = CERTIFICATES / "curved_endpoint_metric_factorization_no_go.json"
REPORT = GENERATED / "curved_endpoint_metric_factorization_no_go.md"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    theorem = EndpointMetricFactorizationNoGo.build(load_system(INPUT))
    certificate = theorem.certificate(dependency_sha256=_sha256(INPUT))
    staged = certificate["staged_solve"]
    outcome = certificate["outcome"]
    checks = {
        "complete invariant family": (
            certificate["ansatz_completeness"]["first_order_dimension"] == 9
            and certificate["ansatz_completeness"]["zeroth_order_dimension"] == 3
            and certificate["ansatz_completeness"]["tracefree_preserving"]
        ),
        "principal symbols agree": staged["order4"]["defects"] == 0,
        "cubic gate exact": (
            staged["order3"]["coefficient_rank"] == 9
            and staged["order3"]["augmented_rank"] == 9
            and staged["order3"]["solution"] == "A_plus=-A_minus"
        ),
        "quadratic polynomial certificate": (
            staged["order2"]["B_minus_plus_B_plus_rank"] == 3
            and staged["order2"][
                "polynomial_nullstellensatz_nonzero_multipliers"
            ]
            > 0
            and staged["order2"]["certificate_multiplier_degree"] == 2
            and staged["order2"]["identity"]
            == "sum_i weight_i constraint_i=1"
            and staged["order2"]["defect"] == 0
        ),
        "later stages correctly unreachable": (
            str(staged["order1"]).startswith("not reached")
            and str(staged["order0"]).startswith("not reached")
        ),
        "scoped no-go": (
            outcome["scalar_principal_factorization_disproved_in_complete_ansatz"]
            and outcome[
                "normally_hyperbolic_same_bundle_factor_pair_disproved_in_this_ansatz"
            ]
            and outcome[
                "complete_parallel_invariant_wave_leading_fibre_family_covered"
            ]
            and not outcome["general_green_hyperbolicity_disproved"]
            and not outcome["curvature_metric_lift_disproved"]
        ),
        "no causal promotion": (
            not outcome["full_factorization_proved"]
            and not outcome["green_claim_promoted"]
            and certificate["status_flags_promoted"] == []
        ),
    }

    if args.guards:
        if certificate["endpoint_backward_witness_coefficients_sha256"] != _sha256(
            INPUT
        ):
            raise AssertionError("endpoint coefficient dependency hash drifted")
        if certificate["schema"] != (
            "pure-weyl-endpoint-metric-scalar-factorization-no-go-v1"
        ):
            raise AssertionError("endpoint factorization schema drifted")

    if not all(checks.values()):
        failed = [name for name, value in checks.items() if not value]
        raise AssertionError(f"endpoint metric factorization checks failed: {failed}")

    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        REPORT.write_text(
            "# Endpoint metric factorization screen\n\n"
            "The exact rank-nine trace-free endpoint has scalar biwave "
            "principal symbol after the endpoint-coordinate normalization is "
            "fixed.  The complete parallel `SO(3)`-invariant two-factor ansatz "
            "contains nine first-order and three algebraic coefficients in "
            "each factor.  Order three forces `A_plus=-A_minus`.  At order "
            "two the three sums `B_minus+B_plus` are fixed, and the remaining "
            "quadratics have an explicit degree-two polynomial "
            "Nullstellensatz certificate "
            "`sum_i w_i f_i=1`.  Hence no factorization exists in this complete "
            "scalar-principal same-bundle family.\n\n"
            "A general nondegenerate parallel invariant leading pair is "
            "covered: the scalar target forces `H_minus H_plus=I`, and a "
            "parallel fibre redistribution reduces it to the tested scalar "
            "principal form without leaving the complete lower-order family. "
            "The no-go still does not exclude mixed-order or enlarged systems, "
            "triangular Green extensions, or the equation-cone curvature-to-"
            "metric causal lift.  No Green or causal flag is promoted.\n",
            encoding="utf-8",
        )
        print("wrote", OUTPUT.relative_to(ROOT))
        print("wrote", REPORT.relative_to(ROOT))

    if not args.emit:
        persisted = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if persisted != certificate:
            raise AssertionError("persisted endpoint factorization certificate drifted")

    for name, value in checks.items():
        print(f"[{'PASS' if value else 'FAIL'}] {name}")
    print(
        "ENDPOINT METRIC FACTORIZATION SCREEN: "
        f"{sum(checks.values())}/{len(checks)} PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
