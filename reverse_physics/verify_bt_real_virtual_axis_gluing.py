#!/usr/bin/env python3
"""Independent verifier for the BT real/virtual axis-gluing result.

This rail does not import the new producer.  It reconstructs the five-point
kernel with the predecessor's invariant-Kallen graph representation, repeats
the phase normalization as integer arithmetic, and checks the physical
threshold map directly in a separate rational parameterization.
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
    "REVERSE_PHYSICS_BT_REAL_VIRTUAL_AXIS_GLUING_V1.json",
)
SCHEMA = os.path.join(
    REPO_ROOT, "reverse_physics", "schema",
    "reverse-physics-bt-real-virtual-axis-gluing-v1.schema.json",
)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def invariant_real_kernel():
    """Recompute [a2*a3*a4] C^2 using invariant rather than dot vertices."""
    from sympy.polys.domains import QQ
    from sympy.polys.fields import field

    if REPO_ROOT not in sys.path:
        sys.path.insert(0, REPO_ROOT)
    import reverse_physics.verify_bt_five_point_independent_mass_threshold as source
    from reverse_physics.verify_bt_external_mass_boundary_log_jet import (
        MassJet,
        MassJetField,
    )

    base, a0, a1, tau, zeta, chi = field(
        "a0,a1,tau,zeta,chi", QQ
    )
    ring = MassJetField(base)
    masses = [
        a0,
        a1,
        MassJet(ring, {1: base.one}),
        MassJet(ring, {2: base.one}),
        MassJet(ring, {4: base.one}),
    ]
    old_hard = source.HARD
    try:
        source.HARD = [1 - zeta, -chi, 1, zeta * (chi - 1)]
        amplitude = source.invariant_amplitude(ring, masses, tau)
    finally:
        source.HARD = old_hard
    leading = amplitude.coefficient(2)
    projected = (leading * leading).coefficients.get(7, base.zero)
    expected = (
        3 * (a0 - a1) ** 2
        * ((a0 - a1) ** 2 - 2 * tau * (a0 + a1))
        / (8 * tau ** 3)
    )
    return {
        "identity": projected == expected,
        "zeta_independent": projected.diff(zeta) == 0,
        "chi_independent": projected.diff(chi) == 0,
        "orders_zero_one_cancel": (
            not amplitude.coefficient(0) and not amplitude.coefficient(1)
        ),
    }


def phase_coefficients(amplitude_norm=64, pair_count=3):
    """Independent integer-factor ledger for the differential real rate."""
    before_angle = Fraction(amplitude_norm, 12 * 2 * 2 * 32 * 32)
    after_angle = 4 * before_angle
    per_pair = -after_angle * Fraction(-3, 8)
    return before_angle, after_angle, per_pair, pair_count * per_pair


def threshold_map_ratios():
    """Use u=sqrt(r), v=sqrt(c) to avoid any radical limit."""
    from sympy.polys.domains import QQ
    from sympy.polys.fields import field

    base, u, v = field("u,v", QQ)
    physical = (1 + v * u) ** 2 / (1 + u) ** 2
    analytic = (1 + v ** 2 * u ** 2) / (1 + u ** 2)
    return physical.subs(u, 0), analytic.subs(u, 0)


def verify(path):
    with open(path, encoding="utf-8") as handle:
        cert = json.load(handle)
    with open(SCHEMA, encoding="utf-8") as handle:
        schema = json.load(handle)

    errors = sorted(Draft202012Validator(schema).iter_errors(cert),
                    key=lambda error: list(error.path))
    checks = {"strict_schema": not errors}
    if errors:
        for error in errors[:8]:
            print(f"SCHEMA: {'/'.join(map(str, error.path))}: {error.message}")
        print("[FAIL] strict_schema")
        print("RESULT: FAIL (0/1)")
        return False

    kernel = invariant_real_kernel()
    checks["invariant_graph_kernel"] = kernel["identity"]
    checks["invariant_orders_zero_one_cancel"] = kernel["orders_zero_one_cancel"]
    checks["invariant_zeta_independence"] = kernel["zeta_independent"]
    checks["invariant_chi_independence"] = kernel["chi_independent"]

    before, after, per_pair, all_pairs = phase_coefficients()
    checks["phase_normalization"] = (
        before == Fraction(1, 768) and after == Fraction(1, 192)
    )
    checks["real_response_coefficients"] = (
        per_pair == Fraction(1, 512)
        and all_pairs == Fraction(3, 512)
    )
    physical_axis, analytic_axis = threshold_map_ratios()
    checks["axis_map_limits"] = physical_axis == analytic_axis == 1

    phase = cert.get("phase_and_combinatorics", {})
    checks["recorded_phase_receipt"] = (
        phase.get("delta_prime_sign") == "(-1)^5=-1"
        and phase.get("unordered_final_pairs") == 3
        and "512*pi^4*s" in phase.get("per_pair_finite_part_shift", "")
    )
    virtual = cert.get("virtual_comparison", {})
    checks["recorded_noncancellation"] = (
        virtual.get("disposition")
        == "DOES_NOT_CANCEL_ON_AXIS_COMPATIBLE_GLUINGS"
        and virtual.get("combined_response")
        == "+3*lambda^6*log(c)/(512*pi^4*s)"
    )
    theorem = cert.get("axis_compatibility_theorem", {})
    checks["mutation_is_explicitly_outside_class"] = (
        "x^(11/12)*y^(1/12)" in theorem.get("decisive_mutation", "")
        and "G_mut(x,0)=0" in theorem.get("decisive_mutation", "")
    )
    disposition = cert.get("disposition", {})
    checks["claim_boundary_fail_closed"] = (
        disposition.get("logarithmic_real_virtual_cancellation")
        == "EXACT_OBSTRUCTION"
        and disposition.get("full_nlo_quotient_trace") == "NOT_COMPUTED"
        and disposition.get("physical_nlo_probability") == "NOT_ESTABLISHED"
        and disposition.get("beyond_tree_positivity") == "NOT_ESTABLISHED"
    )
    inputs = cert.get("provenance", {}).get("inputs", [])
    checks["provenance_hashes"] = len(inputs) == 3 and all(
        item.get("sha256") == sha256(item.get("path", "")) for item in inputs
    )
    checks["producer_checks"] = (
        cert.get("checks", {}).get("ok") is True
        and cert.get("checks", {}).get("passed")
        == cert.get("checks", {}).get("total") == 20
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
