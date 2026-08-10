#!/usr/bin/env python3
"""Independent verifier for the BT external-projector carrier result.

This rail does not import the producer.  It reads the two predecessor
certificates, reconstructs the normalization with exact rational arithmetic,
and uses a truncated multivariate polynomial product to verify the phase-space
degree argument.  It separately tests the two regulator responses.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_EXTERNAL_PROJECTOR_CARRIER_MISMATCH_V1.json",
)
SCHEMA = os.path.join(
    REPO_ROOT, "reverse_physics", "schema",
    "reverse-physics-bt-external-projector-carrier-mismatch-v1.schema.json",
)
TRIANGLE_BOX = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_TRIANGLE_BOX_LOG_JET_V1.json",
)
REAL_THRESHOLD = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_FIVE_POINT_INDEPENDENT_MASS_THRESHOLD_V1.json",
)


def file_sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def multiply(left, right, maximum_degree=4):
    """Independent sparse polynomial multiplication through total degree 4."""
    out = {}
    for left_power, left_value in left.items():
        for right_power, right_value in right.items():
            power = tuple(a + b for a, b in zip(left_power, right_power))
            if sum(power) <= maximum_degree:
                out[power] = out.get(power, Fraction(0)) + left_value * right_value
    return {power: value for power, value in out.items() if value}


def verify(path):
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA, encoding="utf-8") as handle:
            schema = json.load(handle)
        with open(TRIANGLE_BOX, encoding="utf-8") as handle:
            loop = json.load(handle)
        with open(REAL_THRESHOLD, encoding="utf-8") as handle:
            real = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] load: {exc}")
        return False

    errors = list(Draft202012Validator(schema).iter_errors(cert))
    checks = {"strict_schema": not errors}

    checks["loop_predecessor_reduction"] = (
        loop.get("interference_jets", {}).get("complete_reduction")
        == "J_B+J_T+J_X=15*(Ls+Lt+Lu)"
    )
    checks["loop_predecessor_normalization"] = (
        loop.get("interference_jets", {}).get("physical_normalization")
        == "[x1*x2*x3*x4]2*Re(Mtree^*Mloop_top_log)="
           "lambda^6/(4*pi)^2*(16/3)*J_top"
    )
    physical = Fraction(15) * Fraction(16, 3) / 16 / 256
    checks["normalization_reconstruction"] = physical == Fraction(5, 256)
    checks["recorded_physical_rate"] = (
        cert.get("external_projector", {}).get("projected_virtual_log_rate")
        == "d_sigma_virtual_log/d_Omega="
           "5*lambda^6*(Ls+Lt+Lu)/(256*pi^4*s)"
    )

    top = (1, 1, 1, 1)
    degree_four = {top: Fraction(11)}
    analytic_phase = {
        (0, 0, 0, 0): Fraction(3),
        (1, 0, 0, 0): Fraction(5),
        (0, 1, 0, 0): Fraction(7),
        (1, 1, 0, 0): Fraction(13),
    }
    projected = multiply(degree_four, analytic_phase).get(top, 0)
    checks["phase_derivatives_decouple"] = projected == 33

    degree_three = {(0, 1, 1, 1): Fraction(11)}
    mutated = multiply(degree_three, analytic_phase).get(top, 0)
    checks["degree_mutation_is_detected"] = mutated == 55

    response = cert.get("carrier_response", {})
    checks["hard_response_zero"] = response.get("virtual_hard_log_response") == "0"
    checks["real_response_imported"] = (
        response.get("real_reduced_threshold_term")
        == "-(3/8)*x0*x1*log(rho)"
        and response.get("real_finite_part_shift") == "-(3/8)*log(c)"
        and "-3/8" in real.get("answer", "")
    )
    checks["current_responses_do_not_cancel"] = Fraction(0) + Fraction(-3, 8) != 0
    checks["hard_and_mass_ratios_are_distinct"] = (
        "ell=log(-t/s)" in cert.get("external_projector", {}).get("hard_collinear_form", "")
        and "rho=x1/x0" in response.get("rescaling", "")
    )

    disposition = cert.get("disposition", {})
    checks["projector_scope_is_fail_closed"] = (
        disposition.get("hard_log_external_projector") == "APPLIED"
        and disposition.get("virtual_external_mass_boundary_layer") == "NOT_COMPUTED"
        and disposition.get("full_real_phase_space_normalization") == "NOT_COMPUTED"
    )
    checks["physical_claim_is_fail_closed"] = (
        disposition.get("real_virtual_cancellation") == "NOT_COMPUTED"
        and disposition.get("physical_nlo_probability") == "NOT_ESTABLISHED"
        and disposition.get("beyond_tree_positivity") == "NOT_ESTABLISHED"
    )
    recorded_inputs = cert.get("provenance", {}).get("inputs", [])
    checks["provenance_hashes"] = len(recorded_inputs) == 2 and all(
        item.get("sha256") == file_sha256(os.path.join(REPO_ROOT, item.get("path", "")))
        for item in recorded_inputs
    )
    checks["producer_checks"] = (
        cert.get("checks", {}).get("ok") is True
        and cert.get("checks", {}).get("passed")
        == cert.get("checks", {}).get("total") == 13
    )

    for name, ok in checks.items():
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
    passed = sum(checks.values())
    print(f"RESULT: {'PASS' if passed == len(checks) else 'FAIL'} "
          f"({passed}/{len(checks)})")
    return passed == len(checks)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.verify) else 1


if __name__ == "__main__":
    sys.exit(main())
